"""Notices API serializers."""

from rest_framework import serializers

from common.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

from .models import Notice


class AdminNoticeListQuerySerializer(serializers.Serializer):
    """관리자 공지 목록 조회 쿼리 파라미터 검증."""

    type = serializers.ChoiceField(
        choices=["ALL", "URGENT", "NORMAL"],
        default="ALL",
        required=False,
        help_text="공지 유형 필터 (ALL, URGENT, NORMAL)",
    )
    page = serializers.IntegerField(
        default=0,
        min_value=0,
        required=False,
        help_text="페이지 번호 (0부터 시작)",
    )
    size = serializers.IntegerField(
        default=DEFAULT_PAGE_SIZE,
        min_value=1,
        max_value=MAX_PAGE_SIZE,
        required=False,
        help_text="페이지 크기",
    )


class AdminNoticeListItemSerializer(serializers.ModelSerializer):
    """관리자 공지 목록 아이템 응답 스키마."""

    class Meta:
        model = Notice
        fields = [
            "id",
            "type",
            "title",
            "content",
            "image_url",
            "created_at",
            "updated_at",
        ]


class AdminNoticeDetailSerializer(serializers.ModelSerializer):
    """관리자 공지 상세 응답 스키마."""

    class Meta:
        model = Notice
        fields = [
            "id",
            "type",
            "title",
            "content",
            "image_url",
            "created_at",
            "updated_at",
        ]


def to_admin_notice_detail(notice: Notice) -> dict:
    """Notice 모델 인스턴스를 관리자 상세 응답 딕셔너리로 변환합니다."""
    return {
        "id": notice.id,
        "type": notice.type,
        "title": notice.title,
        "content": notice.content,
        "image_url": notice.image_url,
        "created_at": notice.created_at,
        "updated_at": notice.updated_at,
    }


def to_admin_notice_list_item(notice: Notice) -> dict:
    """Notice 모델 인스턴스를 관리자 목록 아이템 딕셔너리로 변환합니다."""
    return to_admin_notice_detail(notice)
