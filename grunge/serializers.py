from furl import furl
from rest_framework import serializers
from rest_framework.reverse import reverse as drf_reverse
from django.db import transaction
from django.db.models import F, Max

from .fields import UUIDHyperlinkedIdentityField
from .models import Album, Artist, Track, Playlist, PlaylistTrack


class TrackAlbumArtistSerializer(serializers.ModelSerializer):
    """
    Serializer for the Artist model used inside Track's Album.
    Includes a read-only UUID and URL field for hyperlinked API representation.
    """

    uuid = serializers.ReadOnlyField()
    url = UUIDHyperlinkedIdentityField(view_name="artist-detail")

    class Meta:
        model = Artist
        fields = ("id", "uuid", "url", "name")



class TrackAlbumSerializer(serializers.ModelSerializer):
    """
    Serializer for the Album model used inside Track.
    Includes nested serialization for the Artist related to the album.
    """

    uuid = serializers.ReadOnlyField()
    url = UUIDHyperlinkedIdentityField(view_name="album-detail")
    artist = TrackAlbumArtistSerializer()

    class Meta:
        model = Album
        fields = ("uuid", "url", "name", "artist")


class TrackSerializer(serializers.ModelSerializer):
    """
    Serializer for the Track model.
    Includes nested Album and Artist information.
    """

    uuid = serializers.ReadOnlyField()
    url = UUIDHyperlinkedIdentityField(view_name="track-detail")
    album = TrackAlbumSerializer()

    class Meta:
        model = Track
        fields = ("uuid", "url", "name", "number", "album")


class AlbumTrackSerializer(TrackSerializer):
    """
    Simplified serializer for Track model used inside Album.
    Excludes nested album/artist detail to reduce response size.
    """

    uuid = serializers.ReadOnlyField()
    url = UUIDHyperlinkedIdentityField(view_name="track-detail")

    class Meta:
        model = Track
        fields = ("uuid", "url", "name", "number")



class AlbumArtistSerializer(serializers.ModelSerializer):
    """
    Serializer for Artist model used inside Album.
    Provides basic artist info and hyperlink.
    """

    uuid = serializers.ReadOnlyField()
    url = UUIDHyperlinkedIdentityField(view_name="artist-detail")

    class Meta:
        model = Artist
        fields = ("uuid", "url", "name")



class AlbumSerializer(serializers.ModelSerializer):
    """
    Serializer for the Album model.
    Includes nested artist and track list.
    """

    uuid = serializers.ReadOnlyField()
    url = UUIDHyperlinkedIdentityField(view_name="album-detail")
    artist = AlbumArtistSerializer()
    tracks = AlbumTrackSerializer(many=True)

    class Meta:
        model = Album
        fields = ("uuid", "url", "name", "year", "artist", "tracks")


class ArtistSerializer(serializers.ModelSerializer):
    """
    Serializer for the Artist model.
    Includes a hyperlink to albums filtered by the artist's UUID.
    """

    uuid = serializers.ReadOnlyField()
    url = UUIDHyperlinkedIdentityField(view_name="artist-detail")
    albums_url = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = ("uuid", "url", "name", "albums_url")

    def get_albums_url(self, artist):
        """
        Generates filtered album list URL for a specific artist.
        """
        path = drf_reverse("album-list", request=self.context["request"])
        return furl(path).set({"artist_uuid": artist.uuid}).url


class PlaylistTrackSerializer(serializers.ModelSerializer):
    """
    Serializer for PlaylistTrack model.
    Maps track UUID, order in the playlist, and read-only track name.
    """

    uuid = serializers.ReadOnlyField(source="track.uuid")
    track = serializers.UUIDField()
    track_name = serializers.CharField(source="track.name", read_only=True)

    class Meta:
        model = PlaylistTrack
        fields = [
            "uuid",
            "track",
            "order",
            "track_name",
        ]

class PlaylistSerializer(serializers.ModelSerializer):
    """
    Serializer for Playlist model.
    Manages creation and update of playlist tracks and their order.
    """

    tracks = PlaylistTrackSerializer(source="playlist_tracks", many=True)

    class Meta:
        model = Playlist
        fields = ["uuid", "name", "tracks"]

    def validate_tracks(self, value):
        track_ids = [item['track'] for item in value]
        if len(track_ids) != len(set(track_ids)):
            raise serializers.ValidationError("Duplicate tracks are not allowed in a playlist.")
        return value


    def create(self, validated_data):
        """
        Creates a new playlist and adds associated tracks in correct order.
        """
        tracks_data = validated_data.pop("playlist_tracks")
        playlist_name = validated_data.get("name")

        playlist, _ = Playlist.objects.get_or_create(
            name=playlist_name, defaults=validated_data
        )

        for track_data in tracks_data:
            self._add_track_to_playlist(playlist, track_data)

        return playlist

    def update(self, instance, validated_data):
        """
        Updates playlist name and its tracks with ordering.
        """
        tracks_data = validated_data.pop("playlist_tracks", None)
        instance.name = validated_data.get("name", instance.name)

        with transaction.atomic():
            instance.save()

            if tracks_data is not None:
                self._update_playlist_tracks(instance, tracks_data)

        return instance

    def _add_track_to_playlist(self, playlist, track_data):
        """
        Helper method to add a track to a playlist, maintaining order.
        """
        order = track_data["order"]
        track_uuid = track_data["track"]
        track = Track.objects.get(uuid=track_uuid)

        if PlaylistTrack.objects.filter(playlist=playlist, track=track).exists():
            return

        max_order = PlaylistTrack.objects.filter(playlist=playlist).aggregate(
            Max("order")
        )["order__max"]

        if max_order is None or order > max_order + 1:
            order = (max_order or 0) + 1

        with transaction.atomic():
            PlaylistTrack.objects.filter(
                playlist=playlist, order__gte=order
            ).order_by("-order").update(order=F("order") + 1)

            PlaylistTrack.objects.create(
                playlist=playlist, track=track, order=order
            )

    def _update_playlist_tracks(self, instance, tracks_data):
    
        instance.playlist_tracks.all().delete()
        playlist_tracks = []
        for item in tracks_data:
            track_instance = Track.objects.get(uuid=item["track"])
            playlist_tracks.append(PlaylistTrack(
                playlist=instance,
                track=track_instance,
                order=item["order"]
            ))
        PlaylistTrack.objects.bulk_create(playlist_tracks)

