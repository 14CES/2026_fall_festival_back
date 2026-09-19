"""Lanterns request and response serializers."""

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import serializers, status

from apps.booths.models import Booth
from common.exceptions import ApiError, InvalidInput, NotFound

from .models import Lantern
from .validators import contains_forbidden_word


class ForbiddenWordValidationMixin:
    def validate_message(self, value):
        if contains_forbidden_word(value):
            raise InvalidInput(
                code="FORBIDDEN_WORD_DETECTED",
                message="부적절한 단어가 포함되어 있습니다.",
            )
        return value


class LanternCreateSerializer(ForbiddenWordValidationMixin, serializers.ModelSerializer):
    lantern_id = serializers.IntegerField(source="id", read_only=True)
    booth_id = serializers.IntegerField()
    nickname = serializers.CharField(max_length=5, required=False, allow_blank=True)
    message = serializers.CharField(max_length=30)

    class Meta:
        model = Lantern
        fields = ["lantern_id", "booth_id", "nickname", "message", "festival_date", "created_at"]
        read_only_fields = ["festival_date", "created_at"]

    def validate(self, attrs):
        today = timezone.localdate()
        # create()에서 같은 값을 재사용한다. Lantern.festival_date의 모델 기본값에 맡기면
        # validate()가 계산한 today와 실제 저장되는 festival_date가 어긋날 수 있어서
        # (모델 default는 값을 임포트 시점에 캡처하므로 이 self._today를 통해 명시적으로 넘긴다)
        self._today = today

        if not (settings.FESTIVAL_START_DATE <= today <= settings.FESTIVAL_END_DATE):
            raise InvalidInput(
                code="NOT_FESTIVAL_PERIOD", message="등불은 축제 당일에만 달 수 있어요."
            )

        booth_id = attrs["booth_id"]
        booth_exists = Booth.objects.filter(
            id=booth_id, deleted_at__isnull=True, place_type="BOOTH"
        ).exists()
        if not booth_exists:
            raise NotFound(code="BOOTH_NOT_FOUND", message="존재하지 않는 부스입니다.")

        user = self.context["request"].user

        # 삭제된 등불은 재등록을 막지 않는다
        # (같은 날 같은 부스라도 삭제 후 재등록 허용 — PM 확인된 정책)
        active_duplicate = Lantern.objects.filter(
            user=user, booth_id=booth_id, festival_date=today, deleted_at__isnull=True
        ).exists()
        if active_duplicate:
            raise ApiError(
                code="DUPLICATE_BOOTH_LANTERN",
                message="부스 선택을 변경해주세요.",
                status_code=status.HTTP_409_CONFLICT,
            )

        today_count = Lantern.objects.filter(user=user, festival_date=today).count()
        if today_count >= 3:
            raise ApiError(
                code="DAILY_LIMIT_EXCEEDED",
                message="등불은 하루에 3개씩만 달 수 있어요.",
                status_code=status.HTTP_409_CONFLICT,
            )

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        booth_id = validated_data["booth_id"]

        with transaction.atomic():
            lantern = Lantern.objects.create(user=user, festival_date=self._today, **validated_data)
            Booth.objects.filter(id=booth_id).update(lantern_count=F("lantern_count") + 1)

        return lantern


class LanternUpdateSerializer(ForbiddenWordValidationMixin, serializers.ModelSerializer):
    lantern_id = serializers.IntegerField(source="id", read_only=True)
    nickname = serializers.CharField(max_length=5, required=False, allow_blank=True)
    message = serializers.CharField(max_length=30, required=False)

    class Meta:
        model = Lantern
        fields = ["lantern_id", "nickname", "message", "updated_at"]
        read_only_fields = ["updated_at"]
