"""Lanterns request and response serializers."""

from rest_framework import serializers, status

from common.exceptions import ApiError

from .models import LanternReport


class LanternReportCreateSerializer(serializers.ModelSerializer):
    report_id = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = LanternReport
        fields = ["report_id", "reason"]

    def validate(self, attrs):
        lantern = self.context["lantern"]
        user = self.context["request"].user

        if LanternReport.objects.filter(lantern=lantern, user=user).exists():
            raise ApiError(
                code="ALREADY_REPORTED",
                message="이미 신고한 등불입니다.",
                status_code=status.HTTP_409_CONFLICT,
            )

        return attrs

    def create(self, validated_data):
        return LanternReport.objects.create(
            lantern=self.context["lantern"],
            user=self.context["request"].user,
            **validated_data,
        )
