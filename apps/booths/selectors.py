"""Read-only booths queries."""

from django.db.models import Case, IntegerField, Prefetch, Value, When

from .constants import BOOTH_CHIP, BOOTH_CHIP_CATEGORIES
from .models import Booth, BoothMenu, BoothOperation


def booth_operations_on(festival_date, time_slot, category=None):
    # UNIQUE(booth, festival_date, time_slot) 제약으로 부스당 최대 1행 보장
    queryset = BoothOperation.objects.filter(
        festival_date=festival_date,
        time_slot=time_slot,
        deleted_at__isnull=True,
        booth__deleted_at__isnull=True,
    ).select_related("booth")

    # '부스' 칩 — 협업 부스(ㄱㄴㄷ순) 먼저, 그 아래 일반 부스(ㄱㄴㄷ순)
    if category == BOOTH_CHIP:
        return (
            queryset.filter(booth__category__in=BOOTH_CHIP_CATEGORIES)
            .annotate(
                collab_order=Case(
                    When(booth__category=Booth.Category.COLLAB, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            )
            .order_by("collab_order", "booth__name")
        )

    # 그 외 — 이름 ㄱㄴㄷ순 (등불 인기 정렬은 부스 랭킹 API가 담당)
    if category:
        queryset = queryset.filter(booth__category=category)
    return queryset.order_by("booth__name")


def booth_detail(booth_id):
    return (
        Booth.objects.filter(pk=booth_id, deleted_at__isnull=True)
        .prefetch_related(
            Prefetch(
                "operations",
                queryset=BoothOperation.objects.filter(deleted_at__isnull=True).order_by(
                    "festival_date", "time_slot"
                ),
            ),
            Prefetch(
                "menus",
                queryset=BoothMenu.objects.filter(deleted_at__isnull=True).order_by("sort_order"),
            ),
        )
        .first()
    )
