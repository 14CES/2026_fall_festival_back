"""Admin Lanterns URL configuration."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.AdminLanternListView.as_view(), name="admin-lantern-list"),
    path("<int:lantern_id>/", views.AdminLanternDetailView.as_view(), name="admin-lantern-detail"),
]
