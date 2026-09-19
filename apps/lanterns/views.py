"""Lanterns API views."""

from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

from common.exceptions import InvalidInput, NotFound, custom_exception_handler
from common.pagination import paginate
from common.permissions import IsAdmin
from common.responses import success_response

from . import selectors
from .serializers import (
    AdminLanternDetailSerializer,
    AdminLanternListQuerySerializer,
    to_admin_lantern_detail,
    to_admin_lantern_list_item,
)


class AdminLanternAPIView(APIView):
    """관리자 등불 API 기본 뷰."""

    permission_classes = [IsAdmin]

    def get_exception_handler(self):
        return custom_exception_handler


class AdminLanternListView(AdminLanternAPIView):
    """관리자 등불 목록 조회 API (GET /api/lanterns/)."""

    @extend_schema(
        tags=["admin-lanterns"],
        summary="관리자 등불 목록 조회",
        operation_id="admin_lantern_list",
        parameters=[AdminLanternListQuerySerializer],
    )
    def get(self, request):
        query_serializer = AdminLanternListQuerySerializer(data=request.query_params)
        if not query_serializer.is_valid():
            raise InvalidInput("입력값이 올바르지 않습니다.", errors=query_serializer.errors)

        sort = query_serializer.validated_data["sort"]
        page = query_serializer.validated_data["page"]
        size = query_serializer.validated_data["size"]

        queryset = selectors.get_admin_lanterns_queryset(sort=sort)
        page_data = paginate(queryset, page=page, size=size)

        lantern_ids = [lantern.id for lantern in page_data.items]
        top_reasons = selectors.get_top_report_reasons_for_lanterns(lantern_ids)

        items = [
            to_admin_lantern_list_item(lantern, top_reasons.get(lantern.id))
            for lantern in page_data.items
        ]

        return success_response(
            "ADMIN_LANTERN_LIST_SUCCESS",
            "관리자 등불 목록 조회에 성공했습니다.",
            {
                "items": items,
                "meta": page_data.as_meta(),
            },
        )


class AdminLanternDetailView(AdminLanternAPIView):
    """관리자 등불 신고 확인 모달 상세 조회 API (GET /api/lanterns/<int:lantern_id>/)."""

    @extend_schema(
        tags=["admin-lanterns"],
        summary="관리자 등불 신고 상세 확인 (모달)",
        operation_id="admin_lantern_detail",
        responses={200: AdminLanternDetailSerializer},
    )
    def get(self, request, lantern_id: int):
        lantern = selectors.get_admin_lantern_by_id(lantern_id=lantern_id)
        if lantern is None:
            raise NotFound("해당 등불을 찾을 수 없습니다.")

        top_reasons = selectors.get_top_report_reasons_for_lanterns([lantern.id])
        top_reason = top_reasons.get(lantern.id)

        return success_response(
            "ADMIN_LANTERN_DETAIL_SUCCESS",
            "관리자 등불 신고 상세 조회에 성공했습니다.",
            to_admin_lantern_detail(lantern, top_reason),
        )
