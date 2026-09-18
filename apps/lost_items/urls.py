"""Lost items API routes (admin, read-only for issue #8)."""

from django.urls import path

from .views import AdminLostItemDetailView, AdminLostItemListView

app_name = "admin_lost_items"

urlpatterns = [
    # 분실물 목록 조회
    path("", AdminLostItemListView.as_view(), name="list"),
    # 분실물 상세 조회
    path("<int:lost_item_id>/", AdminLostItemDetailView.as_view(), name="detail"),
]