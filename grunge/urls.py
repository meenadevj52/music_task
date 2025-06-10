from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter

from .viewsets import (
    AlbumViewSet,
    ArtistViewSet,
    PlaylistViewSet,
    TrackViewSet,
    mainpage,
)

urlpatterns = []


if settings.DJANGO_ADMIN_ENABLED:
    urlpatterns += [
        path("admin/", admin.site.urls),
        path("", mainpage, name="mainpage"),
    ]

if settings.DJANGO_API_ENABLED:
    api_router = DefaultRouter(trailing_slash=False)
    api_router.register("artists", ArtistViewSet)
    api_router.register("albums", AlbumViewSet)
    api_router.register("tracks", TrackViewSet)
    api_router.register(r"playlists", PlaylistViewSet)

    urlpatterns += [
        path("api/<version>/", include(api_router.urls)),
    ]
