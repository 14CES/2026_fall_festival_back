"""Version 1 API routes grouped by business domain."""

from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.accounts.urls")),
    path("admin/auth/", include("apps.admins.urls")),
    path("booths/", include("apps.booths.urls")),
    path("lanterns/", include("apps.lanterns.urls")),
    path("coupons/", include("apps.coupons.urls")),
    path("notices/", include("apps.notices.urls")),
    path("lost-items/", include("apps.lost_items.urls")),
    path("performances/", include("apps.performances.urls")),
]
