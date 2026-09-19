"""Lanterns API views."""

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.accounts.authentication import JWTAuthentication
from common.exceptions import InvalidInput, NotFound, Unauthorized, custom_exception_handler
from common.pagination import paginate
from common.responses import success_response

from . import selectors
from .serializers import LanternListQuerySerializer, to_lantern_item


class LanternAPIView(APIView):
    """등불 조회 API들이 공통으로 상속하는 베이스 뷰.

    get_exception_handler()를 오버라이드해서 공통 에러 응답 형식을 이 앱에만 적용한다
    (apps.lost_items의 LostItemAPIView와 동일한 패턴).
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def get_exception_handler(self):
        return custom_exception_handler


class LanternListView(LanternAPIView):
    """GET /api/lanterns (등불 목록 조회)"""

    def get(self, request):
        query = LanternListQuerySerializer(data=request.query_params)
        if not query.is_valid():
            raise InvalidInput(
                code="INVALID_REQUEST_PARAM",
                message="요청 파라미터가 올바르지 않습니다.",
                errors={key: str(value[0]) for key, value in query.errors.items()},
            )

        params = query.validated_data
        mine = params["mine"]

        if mine and request.user is None:
            raise Unauthorized(message="로그인이 필요합니다.")

        queryset = selectors.lantern_list_queryset(
            user=request.user,
            mine=mine,
            booth_id=params.get("booth_id"),
            festival_date=params.get("date"),
        )

        page = paginate(queryset, page=params["page"], size=params["size"])

        return success_response(
            "LANTERN_LIST_SUCCESS",
            "등불 목록을 조회했습니다.",
            {**page.as_meta(), "items": [to_lantern_item(item) for item in page.items]},
        )


class LanternDetailView(LanternAPIView):
    """GET /api/lanterns/{lantern_id} (등불 단건 조회)"""

    def get(self, request, lantern_id):
        lantern = selectors.get_lantern(lantern_id)
        if lantern is None:
            raise NotFound(code="LANTERN_NOT_FOUND", message="존재하지 않는 등불입니다.")

        is_owner = request.user is not None and lantern.user_id == request.user.id
        if lantern.deleted_at is not None and not is_owner:
            # 본인 것이 아니고 삭제된 상태면 존재하지 않는 것처럼 처리
            raise NotFound(code="LANTERN_NOT_FOUND", message="존재하지 않는 등불입니다.")

        return success_response(
            "LANTERN_DETAIL_SUCCESS",
            "등불을 조회했습니다.",
            to_lantern_item(lantern),
        )
