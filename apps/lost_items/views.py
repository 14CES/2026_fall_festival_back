"""분실물 관리자 API.

- 목록 조회 / 상세 조회
- 등록 / 수정
"""

from drf_spectacular.utils import extend_schema
from rest_framework import status as http_status
from rest_framework.views import APIView

from common.exceptions import InvalidInput, NotFound, custom_exception_handler
from common.pagination import paginate
from common.permissions import IsAdmin
from common.responses import success_response
from common.schema import ErrorResponseSerializer

from . import selectors, services
from .serializers import (
    LostItemDeleteResponseSerializer,
    LostItemDetailResponseSerializer,
    LostItemIdResponseSerializer,
    LostItemListQuerySerializer,
    LostItemListResponseSerializer,
    LostItemUpdateResponseSerializer,
    LostItemWriteSerializer,
    to_detail,
    to_list_item,
)


class AdminLostItemAPIView(APIView):
    """분실물 API 공통 설정."""

    def get_exception_handler(self):
        # 분실물 API에 공통 에러 응답 형식 적용
        return custom_exception_handler


class AdminLostItemListView(AdminLostItemAPIView):
    """분실물 목록 조회 및 등록 API."""

    permission_classes = [IsAdmin]

    @extend_schema(
        tags=["admin-lost-items"],
        summary="분실물 목록 조회 (관리자)",
        operation_id="admin_lost_item_list",
        parameters=[LostItemListQuerySerializer],
        responses={
            200: LostItemListResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def get(self, request):
        # 조회 조건 검증
        query = LostItemListQuerySerializer(data=request.query_params)

        if not query.is_valid():
            raise InvalidInput(
                errors={
                    key: str(value[0])
                    for key, value in query.errors.items()
                }
            )

        params = query.validated_data

        # 조건에 맞는 분실물 조회
        page = paginate(
            selectors.list_lost_items(
                found_date=params.get("found_date")
            ),
            page=params["page"],
            size=params["size"],
        )

        return success_response(
            "LOST_ITEM_LIST_SUCCESS",
            "분실물 목록을 조회했습니다.",
            {
                **page.as_meta(),
                "items": [
                    to_list_item(item)
                    for item in page.items
                ],
            },
        )

    @extend_schema(
        tags=["admin-lost-items"],
        summary="분실물 등록 (관리자)",
        operation_id="admin_lost_item_create",
        request=LostItemWriteSerializer,
        responses={
            201: LostItemIdResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        # 등록 데이터 검증
        serializer = LostItemWriteSerializer(data=request.data)

        if not serializer.is_valid():
            raise InvalidInput(
                errors={
                    key: str(value[0])
                    for key, value in serializer.errors.items()
                }
            )

        # 분실물 등록
        lost_item = services.create_lost_item(
            **serializer.validated_data,
            admin_id=getattr(request, "admin_id", None),
        )

        return success_response(
            "LOST_ITEM_CREATE_SUCCESS",
            "분실물을 등록했습니다.",
            {"lost_item_id": lost_item.pk},
            status=http_status.HTTP_201_CREATED,
        )


class AdminLostItemDetailView(AdminLostItemAPIView):
    """분실물 상세 조회 및 수정 API."""

    permission_classes = [IsAdmin]

    @extend_schema(
        tags=["admin-lost-items"],
        summary="분실물 상세 조회 (관리자)",
        operation_id="admin_lost_item_detail",
        responses={
            200: LostItemDetailResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def get(self, request, lost_item_id):
        # 분실물 조회
        lost_item = selectors.get_lost_item(lost_item_id)

        if lost_item is None:
            raise NotFound(
                code="LOST_ITEM_NOT_FOUND",
                message="분실물을 찾을 수 없습니다.",
            )

        return success_response(
            "LOST_ITEM_DETAIL_SUCCESS",
            "분실물 정보를 조회했습니다.",
            to_detail(lost_item),
        )

    @extend_schema(
        tags=["admin-lost-items"],
        summary="분실물 수정 (관리자)",
        operation_id="admin_lost_item_update",
        request=LostItemWriteSerializer,
        responses={
            200: LostItemUpdateResponseSerializer,
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def put(self, request, lost_item_id):
        # 수정할 분실물 조회
        lost_item = selectors.get_lost_item(lost_item_id)

        if lost_item is None:
            raise NotFound(
                code="LOST_ITEM_NOT_FOUND",
                message="분실물을 찾을 수 없습니다.",
            )

        # 수정 데이터 검증
        serializer = LostItemWriteSerializer(data=request.data)

        if not serializer.is_valid():
            raise InvalidInput(
                errors={
                    key: str(value[0])
                    for key, value in serializer.errors.items()
                }
            )

        # 분실물 수정
        services.update_lost_item(
            lost_item,
            **serializer.validated_data,
        )

        # 변경된 이미지와 태그를 포함해 다시 조회
        updated_item = selectors.get_lost_item(lost_item_id)

        return success_response(
            "LOST_ITEM_UPDATE_SUCCESS",
            "분실물 정보를 수정했습니다.",
            to_detail(updated_item),
        )
        
    @extend_schema(
        tags=["admin-lost-items"],
        summary="분실물 삭제 (관리자)",
        operation_id="admin_lost_item_delete",
        responses={
            200: LostItemDeleteResponseSerializer,
            401: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def delete(self, request, lost_item_id):
        # 삭제할 분실물 조회
        lost_item = selectors.get_lost_item(lost_item_id)
        if lost_item is None:
            raise NotFound(code="LOST_ITEM_NOT_FOUND", message="분실물을 찾을 수 없습니다.")

        # 분실물과 이미지, 태그 Soft Delete
        deleted_at = services.delete_lost_item(lost_item)

        return success_response(
            "LOST_ITEM_DELETE_SUCCESS",
            "분실물을 삭제했습니다.",
            {"lost_item_id": lost_item.pk, "deleted_at": deleted_at},
        )