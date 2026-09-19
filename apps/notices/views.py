"""Notices API views."""

from drf_spectacular.utils import extend_schema
from rest_framework import status as http_status
from rest_framework.views import APIView

from common.exceptions import InvalidInput, custom_exception_handler
from common.permissions import IsAdmin
from common.responses import success_response

from . import services
from .serializers import (
    AdminNoticeCreateSerializer,
    AdminNoticeDetailSerializer,
    to_admin_notice_detail,
)


class AdminNoticeAPIView(APIView):
    """관리자 공지 API 기본 뷰."""

    permission_classes = [IsAdmin]

    def get_exception_handler(self):
        return custom_exception_handler


class AdminNoticeCreateView(AdminNoticeAPIView):
    """관리자 공지사항 신규 등록 API (POST /api/admin/notices/)."""

    @extend_schema(
        tags=["admin-notices"],
        summary="관리자 공지 신규 등록",
        operation_id="admin_notice_create",
        request=AdminNoticeCreateSerializer,
        responses={201: AdminNoticeDetailSerializer},
    )
    def post(self, request):
        serializer = AdminNoticeCreateSerializer(data=request.data)
        if not serializer.is_valid():
            raise InvalidInput("입력값이 올바르지 않습니다.", errors=serializer.errors)

        notice = services.create_notice(
            title=serializer.validated_data["title"],
            content=serializer.validated_data["content"],
            type=serializer.validated_data.get("type", "NORMAL"),
            image_url=serializer.validated_data.get("image_url"),
            admin=getattr(request, "admin", None),
        )

        return success_response(
            "ADMIN_NOTICE_CREATE_SUCCESS",
            "공지사항이 성공적으로 등록되었습니다.",
            to_admin_notice_detail(notice),
            status=http_status.HTTP_201_CREATED,
        )
