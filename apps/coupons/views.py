from datetime import date

from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Coupon,
    DailyCouponCounter,
    User,
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

        today = date.today()

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
