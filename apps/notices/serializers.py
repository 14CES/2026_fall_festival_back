"""Notices API serializers."""

from rest_framework import serializers

from .models import Notice


class AdminNoticeCreateSerializer(serializers.Serializer):
    """관리자 공지사항 등록 요청 바디 검증."""

    type = serializers.ChoiceField(
        choices=Notice.Type.choices,
        default=Notice.Type.NORMAL,
        required=False,
        help_text="공지 유형 (URGENT: 긴급, NORMAL: 일반)",
    )
    title = serializers.CharField(
        max_length=200,
        allow_blank=False,
        trim_whitespace=True,
        help_text="공지 제목",
    )
    content = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
        help_text="공지 본문",
    )
    image_url = serializers.CharField(
        max_length=500,
        required=False,
        allow_null=True,
        allow_blank=True,
        default=None,
        help_text="첨부 사진 URL",
    )


class AdminNoticeDetailSerializer(serializers.ModelSerializer):
    """관리자 공지 상세/생성 응답 스키마."""

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
    """Notice 모델 인스턴스를 관리자 응답 딕셔너리로 변환합니다."""
    return {
        "id": notice.id,
        "type": notice.type,
        "title": notice.title,
        "content": notice.content,
        "image_url": notice.image_url,
        "created_at": notice.created_at,
        "updated_at": notice.updated_at,
    }
