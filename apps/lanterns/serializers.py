"""Lanterns request and response serializers."""
from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import serializers

from apps.booths.models import Booth

from .models import Lantern
from .validators import contains_forbidden_word


class ForbiddenWordValidationMixin:
    def validate_message(self, value):
        if contains_forbidden_word(value):
            raise serializers.ValidationError("부적절한 단어가 포함되어 있습니다.")
        return value


class LanternCreateSerializer(ForbiddenWordValidationMixin, serializers.ModelSerializer):
    lantern_id = serializers.IntegerField(source="id", read_only=True)
    booth_id = serializers.PrimaryKeyRelatedField(
        source="booth",
        queryset=Booth.objects.filter(deleted_at__isnull=True, place_type="BOOTH"),
    )
    nickname = serializers.CharField(max_length=5, required=False, allow_blank=True)
    message = serializers.CharField(max_length=30)

    class Meta:
        model = Lantern
        fields = ["lantern_id", "booth_id", "nickname", "message", "festival_date", "created_at"]
        read_only_fields = ["festival_date", "created_at"]

    def validate(self, attrs):
        today = timezone.localdate()

        if not (settings.FESTIVAL_START_DATE <= today <= settings.FESTIVAL_END_DATE):
            raise serializers.ValidationError("등불은 축제 당일에만 달 수 있어요.")

        user = self.context["request"].user
        booth = attrs["booth"]

        if Lantern.objects.filter(user=user, booth=booth, festival_date=today).exists():
            raise serializers.ValidationError({"booth_id": "부스 선택을 변경해주세요."})

        today_count = Lantern.objects.filter(user=user, festival_date=today).count()
        if today_count >= 3:
            raise serializers.ValidationError("등불은 하루에 3개씩만 달 수 있어요.")

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        booth = validated_data["booth"]

        with transaction.atomic():
            lantern = Lantern.objects.create(user=user, **validated_data)
            Booth.objects.filter(id=booth.id).update(lantern_count=F("lantern_count") + 1)

        return lantern


class LanternUpdateSerializer(ForbiddenWordValidationMixin, serializers.ModelSerializer):
    lantern_id = serializers.IntegerField(source="id", read_only=True)
    nickname = serializers.CharField(max_length=5, required=False, allow_blank=True)
    message = serializers.CharField(max_length=30, required=False)

    class Meta:
        model = Lantern
        fields = ["lantern_id", "nickname", "message", "updated_at"]
        read_only_fields = ["updated_at"]