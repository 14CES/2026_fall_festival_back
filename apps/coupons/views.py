from django.utils import timezone

from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Coupon,
    DailyCouponCounter,
    User,
    WinningNumber,
)
from .serializers import (
    CouponIssueSerializer,
    CouponSerializer,
)


# 쿠폰 발급
class CouponIssueView(APIView):
    @transaction.atomic
    def post(self, request):

        serializer = CouponIssueSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # 같은 유저가 동시에 쿠폰 발급 요청하는 것 방지
        user = User.objects.select_for_update().get(pk=user.pk)

        today = timezone.localdate()

        # 오늘 이미 쿠폰을 받은 적 있는지 확인
        already_issued = Coupon.objects.filter(user=user, issued_date=today).exists()

        if already_issued:
            return Response(
                {"message": "오늘 이미 쿠폰을 발급받았습니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        # 오늘 날짜의 쿠폰 카운터
        counter, created = DailyCouponCounter.objects.get_or_create(
            date=today, defaults={"count": 0}
        )

        # 동시에 여러 명이 발급받아도
        # 같은 daily_sequence가 생기지 않도록 잠금
        counter = DailyCouponCounter.objects.select_for_update().get(pk=counter.pk)

        counter.count += 1

        counter.save(update_fields=["count"])

        # 쿠폰 생성
        coupon = Coupon.objects.create(
            user=user,
            issued_date=today,
            daily_sequence=counter.count,
            status=Coupon.Status.UNSCRATCHED,
        )

        return Response(CouponSerializer(coupon).data, status=status.HTTP_201_CREATED)


# 쿠폰 긁기


class CouponScratchView(APIView):
    @transaction.atomic
    def post(self, request, coupon_id):

        try:
            coupon = Coupon.objects.select_for_update().get(
                coupon_id=coupon_id, deleted_at__isnull=True
            )

        except Coupon.DoesNotExist:
            return Response(
                {"message": "존재하지 않는 쿠폰입니다."}, status=status.HTTP_404_NOT_FOUND
            )

        # 이미 긁은 쿠폰
        if coupon.status != Coupon.Status.UNSCRATCHED:
            return Response(
                {"message": "이미 확인한 쿠폰입니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        # 당일 쿠폰만 스크래치 가능
        if coupon.issued_date != timezone.localdate():
            coupon.status = Coupon.Status.EXPIRED

            coupon.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            data = CouponSerializer(coupon).data
            data["message"] = "기간이 만료된 쿠폰입니다."

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # daily_sequence가 당첨번호 DB에 존재하는지 확인
        is_win = WinningNumber.objects.filter(number=coupon.daily_sequence).exists()

        coupon.scratched_at = timezone.now()

        # 당첨
        if is_win:
            coupon.status = Coupon.Status.WIN

            coupon.save(
                update_fields=[
                    "status",
                    "scratched_at",
                    "updated_at",
                ]
            )

            return Response(CouponSerializer(coupon).data, status=status.HTTP_200_OK)

        # 꽝
        coupon.status = Coupon.Status.LOSE

        coupon.save(
            update_fields=[
                "status",
                "scratched_at",
                "updated_at",
            ]
        )

        return Response(CouponSerializer(coupon).data, status=status.HTTP_200_OK)
