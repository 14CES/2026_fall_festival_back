"""Booths API views."""

from datetime import datetime

from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView

from common.responses import error_response, success_response

from .constants import (
    CATEGORY_CHIPS,
    DAY_NIGHT_BOUNDARY,
    DEFAULT_FESTIVAL_DATE,
    FESTIVAL_DATES,
)
from .models import BoothOperation
from .selectors import booth_detail, booth_operations_on
from .serializers import BoothDetailSerializer, BoothListItemSerializer


# 장소 목록 조회 (지도 핀 + 카드 리스트)
class BoothListView(APIView):
    def get(self, request):
        now = timezone.localtime()

        # 날짜 탭 — 미지정 시 서버 오늘, 축제 기간 외면 첫날
        date_param = request.query_params.get("date")
        if date_param:
            try:
                festival_date = datetime.strptime(date_param, "%Y-%m-%d").date()
            except ValueError:
                return error_response(
                    "INVALID_INPUT",
                    "잘못된 요청값입니다.",
                    {"date": "YYYY-MM-DD 형식으로 입력해주세요."},
                )
            if festival_date not in FESTIVAL_DATES:
                return error_response(
                    "INVALID_FESTIVAL_DATE",
                    "축제 기간 내의 날짜가 아닙니다.",
                    {"date": "2026-09-29 ~ 2026-10-01 중에서 선택해주세요."},
                )
        else:
            today = now.date()
            festival_date = today if today in FESTIVAL_DATES else DEFAULT_FESTIVAL_DATE

        # 주간/야간 탭 — 미지정 시 서버 시각 기준 (16:30 이전 DAY / 이후 NIGHT)
        time_slot = request.query_params.get("time_slot")
        if time_slot:
            if time_slot not in BoothOperation.TimeSlot.values:
                return error_response(
                    "INVALID_INPUT",
                    "잘못된 요청값입니다.",
                    {"time_slot": "DAY 또는 NIGHT 중에서 선택해주세요."},
                )
        else:
            time_slot = (
                BoothOperation.TimeSlot.DAY
                if now.time() < DAY_NIGHT_BOUNDARY
                else BoothOperation.TimeSlot.NIGHT
            )

        # 컬러칩 필터 — 미지정 시 전체. BOOTH 칩은 협업+일반 부스를 묶어서 반환
        category = request.query_params.get("category")
        if category and category not in CATEGORY_CHIPS:
            return error_response(
                "INVALID_INPUT",
                "잘못된 요청값입니다.",
                {"category": "BOOTH / TOILET / ALCOHOL / ECO 중에서 선택해주세요."},
            )

        operations = booth_operations_on(festival_date, time_slot, category)
        items = BoothListItemSerializer(operations, many=True).data

        return success_response(
            "BOOTH_LIST_SUCCESS",
            "장소 목록을 조회했습니다.",
            {
                "festival_date": festival_date.isoformat(),
                "time_slot": time_slot,
                "server_time": now.strftime("%Y-%m-%dT%H:%M:%S"),
                "total_count": len(items),
                "booths": items,
            },
        )


# 장소 상세 조회 (부스 설명 바텀시트)
class BoothDetailView(APIView):
    def get(self, request, booth_id):
        booth = booth_detail(booth_id)

        if booth is None:
            return error_response(
                "BOOTH_NOT_FOUND",
                "장소를 찾을 수 없습니다.",
                status=status.HTTP_404_NOT_FOUND,
            )

        return success_response(
            "BOOTH_DETAIL_SUCCESS",
            "장소 정보를 조회했습니다.",
            BoothDetailSerializer(booth).data,
        )
