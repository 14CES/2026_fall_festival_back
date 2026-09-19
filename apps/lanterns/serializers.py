"""Lanterns request and response serializers."""

from rest_framework import serializers

from apps.lanterns.models import Lantern


class AdminLanternListQuerySerializer(serializers.Serializer):
    """관리자 등불 목록 조회 쿼리 파라미터."""

    sort = serializers.ChoiceField(
        choices=["REPORT_DESC", "LATEST"],
        default="REPORT_DESC",
        required=False,
        help_text="정렬 기준 (REPORT_DESC: 신고 많은 순, LATEST: 최신 등록순)",
    )
    page = serializers.IntegerField(
        min_value=0,
        default=0,
        required=False,
        help_text="페이지 번호 (0부터 시작)",
    )
    size = serializers.IntegerField(
        min_value=1,
        max_value=100,
        default=20,
        required=False,
        help_text="페이지 당 항목 수 (최대 100)",
    )


class AdminLanternListItemSerializer(serializers.Serializer):
    """관리자 등불 목록 항목 스키마."""

    id = serializers.IntegerField()
    nickname = serializers.CharField()
    message = serializers.CharField()
    booth_name = serializers.CharField()
    report_count = serializers.IntegerField()
    top_report_reason = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()


class AdminLanternDetailSerializer(serializers.Serializer):
    """관리자 등불 신고 확인 모달 상세 스키마."""

    id = serializers.IntegerField()
    nickname = serializers.CharField()
    message = serializers.CharField()
    booth_name = serializers.CharField()
    booth_department = serializers.CharField(allow_null=True)
    report_count = serializers.IntegerField()
    top_report_reason = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()


def to_admin_lantern_list_item(lantern: Lantern, top_reason: str | None = None) -> dict:
    """Lantern 모델 인스턴스를 관리자 목록 아이템 딕셔너리로 변환합니다."""
    return {
        "id": lantern.id,
        "nickname": lantern.nickname,
        "message": lantern.message,
        "booth_name": lantern.booth.name if lantern.booth else "",
        "report_count": getattr(lantern, "report_count", 0),
        "top_report_reason": top_reason,
        "created_at": lantern.created_at,
    }


def to_admin_lantern_detail(lantern: Lantern, top_reason: str | None = None) -> dict:
    """Lantern 모델 인스턴스를 관리자 상세 딕셔너리로 변환합니다."""
    return {
        "id": lantern.id,
        "nickname": lantern.nickname,
        "message": lantern.message,
        "booth_name": lantern.booth.name if lantern.booth else "",
        "booth_department": lantern.booth.subtitle if lantern.booth else None,
        "report_count": getattr(lantern, "report_count", 0),
        "top_report_reason": top_reason,
        "created_at": lantern.created_at,
    }
