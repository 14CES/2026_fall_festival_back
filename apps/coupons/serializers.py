from rest_framework import serializers

from .models import Coupon


# 쿠폰 발급 요청
class CouponIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            "user",
        ]


# 쿠폰 응답
class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon

        fields = [
            "coupon_id",
            "user",
            "issued_date",
            "daily_sequence",
            "status",
            "scratched_at",
            "used_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "coupon_id",
            "issued_date",
            "daily_sequence",
            "status",
            "scratched_at",
            "used_at",
            "created_at",
            "updated_at",
        ]
