from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.response import Response

from .filters import AlbumFilter, ArtistFilter, TrackFilter
from .models import Album, Artist, Playlist, Track
from .serializers import (
    AlbumSerializer,
    ArtistSerializer,
    PlaylistSerializer,
    TrackSerializer,
)

class BaseAPIViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Base viewset for read-only APIs using UUID as the lookup field.
    All other read-only viewsets (e.g., Artist, Album, Track) inherit from this class.
    """
    lookup_field = "uuid"
    lookup_url_kwarg = "uuid"



class ArtistViewSet(BaseAPIViewSet):
    """
    API endpoint that allows read-only access to artist data.
    Supports filtering via ArtistFilter.
    """
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    filterset_class = ArtistFilter


class AlbumViewSet(BaseAPIViewSet):
    """
    API endpoint that allows read-only access to album data.
    Supports filtering via AlbumFilter.
    Optimizes query performance using select_related and prefetch_related.
    """
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    filterset_class = AlbumFilter

    def get_queryset(self):
        """
        Optimizes album queries by fetching related artist and tracks in a single DB call.
        """
        queryset = super().get_queryset()
        return queryset.select_related("artist").prefetch_related("tracks")


class TrackViewSet(BaseAPIViewSet):
    """
    API endpoint that allows read-only access to track data.
    Supports filtering via TrackFilter.
    Uses select_related to reduce database queries for album and artist info.
    """
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    filterset_class = TrackFilter

    def get_queryset(self):
        """
        Optimizes track queries by fetching album and artist in one go.
        """
        queryset = super().get_queryset()
        return queryset.select_related("album", "album__artist")



class PlaylistViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows full CRUD operations on playlists.
    Uses UUID for lookup and handles playlist creation, update, and deletion.
    """
    queryset = Playlist.objects.all().order_by("name")
    serializer_class = PlaylistSerializer
    lookup_field = "uuid"

    def perform_destroy(self, instance):
        """
        Overrides deletion behavior to ensure custom response handling.
        """
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



def mainpage(request):
    """
    Renders the main homepage using a simple Django HTML template.
    """
    return render(request, "home.html")

