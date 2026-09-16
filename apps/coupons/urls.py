from django.urls import path

from .views import (
    CouponIssueView,
)

urlpatterns = [
    # 쿠폰 발급
    path("issue/", CouponIssueView.as_view(), name="coupon-issue"),
]
