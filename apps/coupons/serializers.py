from rest_framework import serializers

from .models import (
    BoothVerifyCode,
    Coupon,
)


# 쿠폰 발급 요청
class CouponIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            "user",
        ]


# 목록조회 응답 - 사용 가능 부스 (verify_code는 절대 노출 안 함)
class BoothVerifyCodeBriefSerializer(serializers.ModelSerializer):
    booth_id = serializers.IntegerField(source="id")

    class Meta:
        model = BoothVerifyCode
        fields = [
            "booth_id",
            "booth_name",
        ]


# 나의 쿠폰 목록 조회 응답
class CouponListItemSerializer(serializers.ModelSerializer):
    usable_booths = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = [
            "coupon_id",
            "status",
            "issued_date",
            "usable_booths",
            "scratched_at",
            "used_at",
        ]

    def get_usable_booths(self, obj):
        # WIN/USED가 아니면 부스 목록 안 보여줌
        if obj.status not in (Coupon.Status.WIN, Coupon.Status.USED):
            return None

        booths = BoothVerifyCode.objects.all()

        return BoothVerifyCodeBriefSerializer(booths, many=True).data


# 쿠폰 사용 처리 요청
# user 필드는 CouponIssueSerializer와 동일하게 ModelSerializer로 받아서
# 존재하지 않는 user pk면 자동으로 검증 실패하게 함 (교현님 발급 API와 동일 방식)
class CouponUseSerializer(serializers.ModelSerializer):
    verify_code = serializers.CharField(max_length=20)

    class Meta:
        model = Coupon
        fields = [
            "user",
            "verify_code",
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
        ]

        read_only_fields = [
            "coupon_id",
            "issued_date",
            "daily_sequence",
            "status",
            "scratched_at",
            "used_at",
        ]
