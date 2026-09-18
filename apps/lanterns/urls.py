"""Lanterns API routes."""
from rest_framework.routers import DefaultRouter

from .views import LanternViewSet

router = DefaultRouter()
router.register("lanterns", LanternViewSet, basename="lantern")

urlpatterns = router.urls
