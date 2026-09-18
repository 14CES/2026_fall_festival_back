"""Lanterns API views."""
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied

from apps.booths.models import Booth

from .models import Lantern
from .serializers import LanternCreateSerializer, LanternUpdateSerializer


class LanternViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Lantern.objects.filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return LanternCreateSerializer
        return LanternUpdateSerializer

    def get_object(self):
        obj = super().get_object()
        if obj.user_id != self.request.user.id:
            raise PermissionDenied("본인이 작성한 등불만 수정·삭제할 수 있습니다.")
        return obj

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.deleted_at = timezone.now()
            instance.deleted_by = Lantern.DeletedBy.USER
            instance.save(update_fields=["deleted_at", "deleted_by"])
            Booth.objects.filter(id=instance.booth_id).update(lantern_count=F("lantern_count") - 1)