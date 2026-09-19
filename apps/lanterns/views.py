"""Lanterns API views."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.accounts.authentication import JWTAuthentication
from common.exceptions import InvalidInput, NotFound, custom_exception_handler
from common.responses import success_response

from . import selectors
from .serializers import LanternReportCreateSerializer


class LanternViewSet(viewsets.GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_exception_handler(self):
        return custom_exception_handler

    @action(detail=True, methods=["post"], url_path="reports")
    def report(self, request, pk=None):
        lantern = selectors.get_active_lantern(pk)
        if lantern is None:
            raise NotFound(code="LANTERN_NOT_FOUND", message="존재하지 않는 등불입니다.")

        serializer = LanternReportCreateSerializer(
            data=request.data, context={"request": request, "lantern": lantern}
        )
        if not serializer.is_valid():
            raise InvalidInput(
                code="INVALID_REQUEST_PARAM",
                message="reason 값이 올바르지 않습니다.",
                errors={key: str(value[0]) for key, value in serializer.errors.items()},
            )
        serializer.save()

        return success_response(
            "LANTERN_REPORT_SUCCESS",
            "신고가 접수되었습니다.",
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
