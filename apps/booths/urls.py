"""Booths API routes."""

from django.urls import path

from .views import BoothListView

urlpatterns = [
    # 장소 목록 조회 (지도 핀 + 카드 리스트)
    path("", BoothListView.as_view(), name="booth-list"),
]
