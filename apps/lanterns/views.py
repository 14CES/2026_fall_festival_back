"""Lanterns API views."""

from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from apps.accounts.authentication import JWTAuthentication
from common.exceptions import InvalidInput, NotFound, Unauthorized, custom_exception_handler
from common.pagination import paginate
from common.responses import success_response

from . import selectors
from .serializers import LanternListQuerySerializer, to_lantern_item


class LanternViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def get_exception_handler(self):
        return custom_exception_handler

    def list(self, request, *args, **kwargs):
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

    def retrieve(self, request, *args, **kwargs):
        lantern = selectors.get_lantern(self.kwargs["pk"])
        if lantern is None:
            raise NotFound(code="LANTERN_NOT_FOUND", message="존재하지 않는 등불입니다.")

        is_owner = request.user is not None and lantern.user_id == request.user.id
        if lantern.deleted_at is not None and not is_owner:
            raise NotFound(code="LANTERN_NOT_FOUND", message="존재하지 않는 등불입니다.")

        return success_response(
            "LANTERN_DETAIL_SUCCESS",
            "등불을 조회했습니다.",
            to_lantern_item(lantern),
        )
