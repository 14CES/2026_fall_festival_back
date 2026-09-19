"""Lanterns API views."""

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.authentication import JWTAuthentication
from apps.booths.models import Booth
from common.exceptions import ApiError, NotFound, custom_exception_handler
from common.responses import success_response

from .models import Lantern
from .serializers import LanternCreateSerializer, LanternUpdateSerializer


class LanternViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Lantern.objects.all()

    def get_exception_handler(self):
        return custom_exception_handler

    def get_serializer_class(self):
        if self.request.method == "POST":
            return LanternCreateSerializer
        return LanternUpdateSerializer

    def get_object(self):
        try:
            obj = Lantern.objects.get(pk=self.kwargs["pk"])
        except Lantern.DoesNotExist as exc:
            raise NotFound(code="LANTERN_NOT_FOUND", message="존재하지 않는 등불입니다.") from exc

        if obj.user_id != self.request.user.id:
            raise ApiError(
                code="NOT_OWNER",
                message="본인이 작성한 등불만 수정·삭제할 수 있습니다.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if obj.deleted_at is not None:
            raise ApiError(
                code="ALREADY_DELETED",
                message="이미 삭제된 등불입니다.",
                status_code=status.HTTP_409_CONFLICT,
            )

        return obj

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            code="LANTERN_CREATE_SUCCESS",
            message="등불을 성공적으로 남겼어요!",
            data=serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        if instance.festival_date != timezone.localdate():
            raise ApiError(
                code="NOT_TODAY_LANTERN",
                message="지난 등불은 수정할 수 없어요.",
                status_code=status.HTTP_409_CONFLICT,
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            code="LANTERN_UPDATE_SUCCESS",
            message="등불이 수정되었습니다.",
            data=serializer.data,
        )

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.deleted_at = timezone.now()
            instance.deleted_by = Lantern.DeletedBy.USER
            instance.save(update_fields=["deleted_at", "deleted_by"])
            Booth.objects.filter(id=instance.booth_id).update(lantern_count=F("lantern_count") - 1)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(
            code="LANTERN_DELETE_SUCCESS",
            message="등불이 삭제되었습니다.",
            data=None,
        )
