"""Read-only booths queries."""

from django.db.models import (
    Case,
    Exists,
    IntegerField,
    OuterRef,
    Prefetch,
    Q,
    Sum,
    Value,
    When,
)

from apps.lanterns.models import Lantern

from .constants import BOOTH_CHIP, BOOTH_CHIP_CATEGORIES
from .models import Booth, BoothMenu, BoothOperation


def _my_lantern_exists(user, booth_ref):
    # 해당 부스에 로그인 사용자의 삭제되지 않은 등불이 있는지 (서브쿼리)
    return Exists(
        Lantern.objects.filter(booth_id=OuterRef(booth_ref), user=user, deleted_at__isnull=True)
    )


def booth_operations_on(festival_date, time_slot, category=None, user=None):
    # UNIQUE(booth, festival_date, time_slot) 제약으로 부스당 최대 1행 보장
    queryset = BoothOperation.objects.filter(
        festival_date=festival_date,
        time_slot=time_slot,
        deleted_at__isnull=True,
        booth__deleted_at__isnull=True,
    ).select_related("booth")

    # '부스' 칩 — 협업 부스(ㄱㄴㄷ순) 먼저, 그 아래 일반 부스(ㄱㄴㄷ순)
    if category == BOOTH_CHIP:
        queryset = (
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
    else:
        # 그 외 — 이름 ㄱㄴㄷ순 (등불 인기 정렬은 부스 랭킹 API가 담당)
        if category:
            queryset = queryset.filter(booth__category=category)
        queryset = queryset.order_by("booth__name")

    if user is not None:
        queryset = queryset.annotate(has_my_lantern=_my_lantern_exists(user, "booth_id"))
    return queryset


def booth_detail(booth_id, user=None):
    queryset = Booth.objects.filter(pk=booth_id, deleted_at__isnull=True).prefetch_related(
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
    if user is not None:
        queryset = queryset.annotate(has_my_lantern=_my_lantern_exists(user, "pk"))
    return queryset.first()


def booth_search(keyword, festival_date=None, time_slot=None, user=None):
    # 부스명/소속/위치/소개/메뉴명 부분 일치 OR 검색. 메뉴 매칭은 중복 제거
    match = (
        Q(name__icontains=keyword)
        | Q(subtitle__icontains=keyword)
        | Q(location_detail__icontains=keyword)
        | Q(description__icontains=keyword)
        | Q(menus__name__icontains=keyword, menus__deleted_at__isnull=True)
    )
    queryset = Booth.objects.filter(match, deleted_at__isnull=True)

    if festival_date:
        operating = Q(operations__festival_date=festival_date, operations__deleted_at__isnull=True)
        if time_slot:
            operating &= Q(operations__time_slot=time_slot)
        queryset = queryset.filter(operating)

    # 정렬: 부스명 정확 일치 → 부스명 부분 일치 → 그 외, 같은 그룹 안에서는 이름 ㄱㄴㄷ순
    queryset = queryset.annotate(
        match_rank=Case(
            When(name__iexact=keyword, then=Value(0)),
            When(name__icontains=keyword, then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        )
    )
    if user is not None:
        queryset = queryset.annotate(has_my_lantern=_my_lantern_exists(user, "pk"))
    return queryset.distinct().order_by("match_rank", "name")


def booth_ranking(limit):
    # 등불 달기 대상(place_type=BOOTH)만 랭킹에 포함
    return list(
        Booth.objects.filter(place_type=Booth.PlaceType.BOOTH, deleted_at__isnull=True).order_by(
            "-lantern_count", "name"
        )[:limit]
    )


def total_lantern_count():
    result = Booth.objects.filter(
        place_type=Booth.PlaceType.BOOTH, deleted_at__isnull=True
    ).aggregate(total=Sum("lantern_count"))
    return result["total"] or 0
