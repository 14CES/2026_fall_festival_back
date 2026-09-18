"""Lost items API views (administrator side, read-only for issue #8).

POST/PUT/DELETE and image upload land in follow-up issues; this module only
adds the two GET methods so those PRs stay additive.
"""

from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

from common.exceptions import InvalidInput, NotFound, custom_exception_handler
from common.pagination import paginate
from common.permissions import IsAdmin
from common.responses import success_response
from common.schema import ErrorResponseSerializer

from . import selectors
from .serializers import (
    LostItemDetailResponseSerializer,
    LostItemListQuerySerializer,
    LostItemListResponseSerializer,
    to_detail,
    to_list_item,
)

from rest_framework.permissions import AllowAny
from .serializers import (
    UserLostItemListQuerySerializer,
    UserLostItemDetailResponseSerializer,
    to_user_detail,
)


class AdminLostItemAPIView(APIView):
    """Base for this app's admin views.

    Opts this app into the shared ``{success, code, message, errors}`` error
    envelope *without* registering it globally in
    ``REST_FRAMEWORK["EXCEPTION_HANDLER"]`` — that would also change error
    responses for apps.coupons and anything else already relying on DRF's
    default shape. If the team decides to standardize project-wide, replace
    this override with the global setting (see common/exceptions.py).
    """

    def get_exception_handler(self):
        return custom_exception_handler


class AdminLostItemListView(AdminLostItemAPIView):
    """GET /api/admin/lost-items/"""

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
        query = LostItemListQuerySerializer(data=request.query_params)
        if not query.is_valid():
            raise InvalidInput(errors={key: str(value[0]) for key, value in query.errors.items()})

        params = query.validated_data
        page = paginate(
            selectors.list_lost_items(found_date=params.get("found_date")),
            page=params["page"],
            size=params["size"],
        )

        return success_response(
            "LOST_ITEM_LIST_SUCCESS",
            "분실물 목록을 조회했습니다.",
            {**page.as_meta(), "items": [to_list_item(item) for item in page.items]},
        )


class AdminLostItemDetailView(AdminLostItemAPIView):
    """GET /api/admin/lost-items/{lost_item_id}/"""

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
        lost_item = selectors.get_lost_item(lost_item_id)
        if lost_item is None:
            raise NotFound(code="LOST_ITEM_NOT_FOUND", message="분실물을 찾을 수 없습니다.")

        return success_response(
            "LOST_ITEM_DETAIL_SUCCESS",
            "분실물 정보를 조회했습니다.",
            to_detail(lost_item),
        )

class LostItemAPIView(APIView):
    """사용자용 View의 기본 클래스"""
    permission_classes = [AllowAny]

    def get_exception_handler(self):
        return custom_exception_handler


class UserLostItemListView(LostItemAPIView):
    """GET /api/lost-items/ (사용자 분실물 목록 조회)"""

    @extend_schema(
        tags=["lost-items"],
        summary="분실물 목록 조회 (사용자)",
        operation_id="user_lost_item_list",
        parameters=[UserLostItemListQuerySerializer],
        responses={
            200: LostItemListResponseSerializer,
            400: ErrorResponseSerializer,
        },
    )
    def get(self, request):
        query = UserLostItemListQuerySerializer(data=request.query_params)
        if not query.is_valid():
            raise InvalidInput(errors={key: str(value[0]) for key, value in query.errors.items()})

        params = query.validated_data
        page = paginate(
            selectors.list_lost_items(
                found_date=params.get("found_date"),
                keyword=params.get("keyword")
            ),
            page=params["page"],
            size=params["size"],
        )

        return success_response(
            "LOST_ITEM_LIST_SUCCESS",
            "분실물 목록을 조회했습니다.",
            {**page.as_meta(), "items": [to_list_item(item) for item in page.items]},
        )


class UserLostItemDetailView(LostItemAPIView):
    """GET /api/lost-items/{lost_item_id}/ (사용자 분실물 상세 조회)"""

    @extend_schema(
        tags=["lost-items"],
        summary="분실물 상세 조회 (사용자)",
        operation_id="user_lost_item_detail",
        responses={
            200: UserLostItemDetailResponseSerializer,
            404: ErrorResponseSerializer,
        },
    )
    def get(self, request, lost_item_id):
        lost_item = selectors.get_lost_item(lost_item_id)
        if lost_item is None:
            raise NotFound(code="LOST_ITEM_NOT_FOUND", message="해당 분실물을 찾을 수 없습니다.")

        return success_response(
            "LOST_ITEM_DETAIL_SUCCESS",
            "분실물 상세 정보를 조회했습니다.",
            to_user_detail(lost_item),
        )