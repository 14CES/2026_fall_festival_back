"""Read-only lanterns queries."""

from .models import Lantern


def lantern_list_queryset(*, user, mine, booth_id=None, festival_date=None):
    """mine=True면 본인 것(삭제 포함), False면 공개 목록(삭제 제외)."""
    if mine:
        queryset = Lantern.objects.filter(user=user)
    else:
        queryset = Lantern.objects.filter(deleted_at__isnull=True)

    if booth_id is not None:
        queryset = queryset.filter(booth_id=booth_id)
    if festival_date is not None:
        queryset = queryset.filter(festival_date=festival_date)

    return queryset.order_by("-created_at")


def get_lantern(lantern_id):
    """id로 조회, 없으면 None."""
    return Lantern.objects.filter(pk=lantern_id).first()
