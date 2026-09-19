"""Notices URL configuration."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.AdminNoticeCreateView.as_view(), name="admin-notice-create"),
]
