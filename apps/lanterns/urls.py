"""Lanterns API routes."""

from django.urls import path

from .views import LanternDetailView, LanternListView

urlpatterns = [
    path("", LanternListView.as_view(), name="lantern-list"),
    path("<int:lantern_id>/", LanternDetailView.as_view(), name="lantern-detail"),
]
