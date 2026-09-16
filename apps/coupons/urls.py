from django.urls import path

from .views import (
    CouponIssueView,
    CouponScratchView,
)

urlpatterns = [
    # 쿠폰 발급
    path("issue/", CouponIssueView.as_view(), name="coupon-issue"),
    # 쿠폰 긁기
    path("<int:coupon_id>/scratch/", CouponScratchView.as_view(), name="coupon-scratch"),
]
