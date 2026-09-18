"""Root URL configuration."""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/coupons/", include("apps.coupons.urls")),
    path("api/admin/lost-items/", include("apps.lost_items.urls")),
    path("api/booths/", include("apps.booths.urls")),
]
