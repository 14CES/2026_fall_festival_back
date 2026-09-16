"""Root URL configuration."""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from api.health import health_check

urlpatterns = [
    path("api/health/", health_check, name="health-check"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/", include("api.v1.urls")),
    path("api/coupons/", include("apps.coupons.urls")),
]
