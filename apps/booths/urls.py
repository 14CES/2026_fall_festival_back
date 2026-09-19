"""Booths API routes."""

from django.urls import path

from .views import BoothDetailView, BoothListView, BoothRankingView, BoothSearchView

urlpatterns = [
    # 장소 목록 조회 (지도 핀 + 카드 리스트)
    path("", BoothListView.as_view(), name="booth-list"),
    # 장소 상세 조회 (부스 설명 바텀시트)
    path("<int:booth_id>/", BoothDetailView.as_view(), name="booth-detail"),
    # 장소 검색 (검색 모달)
    path("search/", BoothSearchView.as_view(), name="booth-search"),
    # 부스 등불 랭킹 (홈 화면)
    path("ranking/", BoothRankingView.as_view(), name="booth-ranking"),
]
