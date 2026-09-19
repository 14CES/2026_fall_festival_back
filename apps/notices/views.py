"""Notices API views."""

from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

from common.exceptions import InvalidInput, NotFound, custom_exception_handler
from common.pagination import paginate
from common.permissions import IsAdmin
from common.responses import success_response

from . import selectors
from .serializers import (
    AdminNoticeDetailSerializer,
    AdminNoticeListQuerySerializer,
    to_admin_notice_detail,
    to_admin_notice_list_item,
)


class AdminNoticeAPIView(APIView):
    """관리자 공지 API 기본 뷰."""

    permission_classes = [IsAdmin]

    def get_exception_handler(self):
        return custom_exception_handler


class AdminNoticeListView(AdminNoticeAPIView):
    """관리자 공지사항 목록 조회 API (GET /api/admin/notices/)."""

    @extend_schema(
        tags=["admin-notices"],
        summary="관리자 공지 목록 조회",
        operation_id="admin_notice_list",
        parameters=[AdminNoticeListQuerySerializer],
    )
    def get(self, request):
        query_serializer = AdminNoticeListQuerySerializer(data=request.query_params)
        if not query_serializer.is_valid():
            raise InvalidInput("입력값이 올바르지 않습니다.", errors=query_serializer.errors)

        notice_type = query_serializer.validated_data["type"]
        page = query_serializer.validated_data["page"]
        size = query_serializer.validated_data["size"]

        queryset = selectors.get_admin_notices_queryset(notice_type=notice_type)
        page_data = paginate(queryset, page=page, size=size)

        items = [to_admin_notice_list_item(notice) for notice in page_data.items]
        return success_response(
            "ADMIN_NOTICE_LIST_SUCCESS",
            "공지 목록 조회에 성공했습니다.",
            {
                "items": items,
                "meta": page_data.as_meta(),
            },
        )


class AdminNoticeDetailView(AdminNoticeAPIView):
    """관리자 공지사항 상세 조회 API (GET /api/admin/notices/<int:notice_id>/)."""

    @extend_schema(
        tags=["admin-notices"],
        summary="관리자 공지 상세 조회",
        operation_id="admin_notice_detail",
        responses={200: AdminNoticeDetailSerializer},
    )
    def get(self, request, notice_id: int):
        notice = selectors.get_notice_by_id(notice_id=notice_id)
        if notice is None:
            raise NotFound("해당 공지사항을 찾을 수 없습니다.")

        return success_response(
            "ADMIN_NOTICE_DETAIL_SUCCESS",
            "공지 상세 조회에 성공했습니다.",
            to_admin_notice_detail(notice),
        )
