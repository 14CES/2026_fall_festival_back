"""Lanterns request and response serializers."""

from django.utils import timezone
from rest_framework import serializers

from common.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

from .models import Lantern


class LanternListQuerySerializer(serializers.Serializer):
    mine = serializers.BooleanField(required=False, default=False)
    booth_id = serializers.IntegerField(required=False)
    date = serializers.DateField(required=False)
    page = serializers.IntegerField(required=False, min_value=0, default=0)
    size = serializers.IntegerField(
        required=False, min_value=1, max_value=MAX_PAGE_SIZE, default=DEFAULT_PAGE_SIZE
    )


def _lantern_status(lantern):
    if lantern.deleted_at is None:
        return "active"
    if lantern.deleted_by == Lantern.DeletedBy.ADMIN:
        return "deleted_by_admin"
    return "deleted_by_user"


def to_lantern_item(lantern):
    status = _lantern_status(lantern)
    return {
        "lantern_id": lantern.id,
        "booth_id": lantern.booth_id,
        "nickname": lantern.nickname,
        "message": lantern.message if status == "active" else None,
        "status": status,
        "created_at": timezone.localtime(lantern.created_at).strftime("%Y-%m-%dT%H:%M:%S"),
    }
