"""Shared permission primitives.

Admin authentication is still pending the ``apps.admins`` decision, so this
checks a shared bearer token from settings. The interface (``request.admin_id``)
is what the views depend on, so swapping in the real admin model later touches
only this file.
"""

from django.conf import settings
from rest_framework.permissions import BasePermission

from .exceptions import Unauthorized


class IsAdmin(BasePermission):
    """Require ``Authorization: Bearer {admin_token}``."""

    def has_permission(self, request, view):
        header = request.headers.get("Authorization", "")
        scheme, _, token = header.partition(" ")

        expected = getattr(settings, "ADMIN_API_TOKEN", "")
        if scheme.lower() != "bearer" or not token.strip() or not expected:
            raise Unauthorized()
        if token.strip() != expected:
            raise Unauthorized()

        # TODO(admins): replace with the authenticated Admin instance once
        #   apps.admins lands; views only read request.admin_id.
        request.admin_id = None
        return True