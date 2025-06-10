from rest_framework import viewsets
from rest_framework.response import Response
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from grunge.models import Album, Artist, Playlist, PlaylistTrack, Track
from grunge.serializers import PlaylistSerializer

from rest_framework import status
from django.urls import reverse

from grunge.models import Artist, Album, Track, Playlist, PlaylistTrack
import uuid



class PlaylistViewSet(viewsets.ModelViewSet):
    """
    A viewset for handling CRUD operations on Playlist objects.
    """

    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    lookup_field = "uuid"

    def perform_destroy(self, instance):
        """
        Perform the deletion of the playlist instance.
        """
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlaylistTrackSerializerTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.artist1 = Artist.objects.create(name="Artist 1")
        self.artist2 = Artist.objects.create(name="Artist 2")
        
        self.album1 = Album.objects.create(name="Album 1", year=2020, artist=self.artist1)
        self.album2 = Album.objects.create(name="Album 2", year=2021, artist=self.artist2)

        self.track1 = Track.objects.create(name="Track 1", album=self.album1, number=1)
        self.track2 = Track.objects.create(name="Track 2", album=self.album1, number=2)
        self.track3 = Track.objects.create(name="Track 3", album=self.album2, number=1)

        self.playlist1 = Playlist.objects.create(name="Playlist 1")
        self.playlist2 = Playlist.objects.create(name="Playlist 2")
        
       
        self.playlist = self.playlist1

        self.playlist_track1 = PlaylistTrack.objects.create(
            playlist=self.playlist1, track=self.track1, order=1
        )
        self.playlist_track2 = PlaylistTrack.objects.create(
            playlist=self.playlist1, track=self.track2, order=2
        )
        self.playlist_track3 = PlaylistTrack.objects.create(
            playlist=self.playlist2, track=self.track3, order=1
        )

    def test_create_playlist_with_tracks(self):
        playlist_data = {
            "name": "Test Playlist",
            "tracks": [
                {"track": str(self.track1.uuid), "order": 1},
                {"track": str(self.track2.uuid), "order": 2},
            ],
        }
        response = self.client.post(
            reverse("playlist-list", kwargs={"version": "v1"}),
            playlist_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Playlist.objects.count(), 3)
        self.assertEqual(
            PlaylistTrack.objects.filter(playlist__name="Test Playlist").count(), 2
        )


    def test_update_playlist_tracks(self):
        playlist = Playlist.objects.create(name="Test Playlist")
        PlaylistTrack.objects.create(playlist=playlist, track=self.track1, order=1)

        updated_playlist_data = {
        "name": "Updated Playlist",
        "tracks": [
            {"track": str(self.track2.uuid), "order": 1},
            {"track": str(self.track3.uuid), "order": 2},
        ],
        }

        response = self.client.put(
            reverse("playlist-detail", kwargs={"version": "v1", "uuid": str(playlist.uuid)}),
            updated_playlist_data,
            format="json",
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PlaylistTrack.objects.filter(playlist=playlist).count(), 2)
        self.assertEqual(
            PlaylistTrack.objects.get(playlist=playlist, track=self.track2).order, 1
        )
    
    def test_partial_update_playlist_name(self):
        playlist = Playlist.objects.create(name="Original Playlist")
        PlaylistTrack.objects.create(playlist=playlist, track=self.track1, order=1)

        patch_data = {"name": "Renamed Playlist"}
        url = reverse("playlist-detail", kwargs={"version": "v1", "uuid": str(playlist.uuid)})
        response = self.client.patch(url, patch_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        playlist.refresh_from_db()
        self.assertEqual(playlist.name, "Renamed Playlist")
        self.assertEqual(playlist.playlist_tracks.count(), 1)

    def test_create_playlist_without_name(self):
        playlist_data = {
            "tracks": [
                {"track": str(self.track1.uuid), "order": 1}
            ]
        }
        response = self.client.post(
            reverse("playlist-list", kwargs={"version": "v1"}),
            playlist_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_playlist_with_tracks_from_multiple_albums(self):
        playlist_data = {
            "name": "Multi Album Playlist",
            "tracks": [
                {"track": str(self.track1.uuid), "order": 1},
                {"track": str(self.track3.uuid), "order": 2},  # different album/artist
            ]
        }
        response = self.client.post(
            reverse("playlist-list", kwargs={"version": "v1"}),
            playlist_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_playlist_with_empty_track_dict(self):
        playlist_data = {
            "name": "Playlist With Empty Track Dict",
            "tracks": [{}]
        }
        response = self.client.post(
            reverse("playlist-list", kwargs={"version": "v1"}),
            playlist_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    

    def test_get_invalid_playlist_uuid(self):
        url = reverse("playlist-detail", kwargs={"version": "v1", "uuid": str(uuid.uuid4())})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_duplicate_track_in_playlist(self):
        playlist_data = {
            "name": "Duplicate Track Playlist",
            "tracks": [
                {"track": str(self.track1.uuid), "order": 1},
                {"track": str(self.track1.uuid), "order": 2},
            ],
        }
        response = self.client.post(
            reverse("playlist-list", kwargs={"version": "v1"}),
            playlist_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_playlists(self):
        url = reverse('playlist-list', kwargs={'version': 'v1'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(p['name'] == self.playlist.name for p in response.json()['results']))

    def test_search_playlists(self):
        url = reverse('playlist-list', kwargs={'version': 'v1'}) + '?search=Playlist'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()['results']
        self.assertTrue(any(p['name'] == self.playlist.name for p in results))

    def test_get_playlist(self):
        url = reverse('playlist-detail', kwargs={'version': 'v1', 'uuid': self.playlist.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], self.playlist.name)

    def test_order_adjustment(self):
        playlist_data = {
            "name": "Order Adjustment Playlist",
            "tracks": [
                {"track": str(self.track1.uuid), "order": 5},
                {"track": str(self.track2.uuid), "order": 1},
            ],
        }
        response = self.client.post(
            reverse("playlist-list", kwargs={"version": "v1"}),
            playlist_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        playlist = Playlist.objects.get(name="Order Adjustment Playlist")
        self.assertEqual(
            PlaylistTrack.objects.get(playlist=playlist, track=self.track1).order, 2
        )


    def test_invalid_data(self):
        invalid_playlist_data = {
            "name": "Invalid Playlist",
            "tracks": [{"track": "invalid-uuid", "order": 1}],

        }
        response = self.client.post(
            reverse("playlist-list", kwargs={"version": "v1"}),
            invalid_playlist_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_empty_playlist(self):
        empty_playlist_data = {"name": "Empty Playlist", "tracks": []}
        response = self.client.post(
            reverse("playlist-list", kwargs={"version": "v1"}),
            empty_playlist_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Playlist.objects.filter(name="Empty Playlist").count(), 1)

    def test_delete_playlist(self):
        playlist = Playlist.objects.create(name="Deletable Playlist")
        PlaylistTrack.objects.create(playlist=playlist, track=self.track1, order=1)
        url = reverse("playlist-detail", kwargs={"version": "v1", "uuid": str(playlist.uuid)})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Playlist.objects.filter(uuid=playlist.uuid).exists())
        self.assertFalse(PlaylistTrack.objects.filter(playlist=playlist).exists())

    def test_cascade_delete_playlist_tracks(self):
        playlist = Playlist.objects.create(name="Cascade Delete Test")
        PlaylistTrack.objects.create(playlist=playlist, track=self.track1, order=1)

        self.assertEqual(PlaylistTrack.objects.filter(playlist=playlist).count(), 1)

        url = reverse("playlist-detail", kwargs={"version": "v1", "uuid": str(playlist.uuid)})
        self.client.delete(url)

        self.assertEqual(PlaylistTrack.objects.filter(playlist=playlist).count(), 0)
        
    def test_missing_order_field(self):
        playlist_data = {
            "name": "Missing Order",
            "tracks": [{"track": str(self.track1.uuid)}]
        }
        response = self.client.post(
            reverse("playlist-list", kwargs={"version": "v1"}), playlist_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_missing_track_field(self):
        playlist_data = {
            "name": "Missing Track",
            "tracks": [{"order": 1}]
        }
        response = self.client.post(
            reverse("playlist-list", kwargs={"version": "v1"}), playlist_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_non_integer_order(self):
        playlist_data = {
            "name": "Invalid Order Type",
            "tracks": [{"track": str(self.track1.uuid), "order": "first"}]
        }
        response = self.client.post(
            reverse("playlist-list", kwargs={"version": "v1"}), playlist_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_missing_track_key(self):
        playlist_data = {
            "name": "Missing Track Key",
            "tracks": [{"order": 1}]
        }
        response = self.client.post(
            reverse("playlist-list", kwargs={"version": "v1"}),
            playlist_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    
    def test_missing_order_key(self):
        playlist_data = {
            "name": "Missing Order Key",
            "tracks": [{"track": str(self.track1.uuid)}]
        }
        response = self.client.post(
            reverse("playlist-list", kwargs={"version": "v1"}),
            playlist_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

