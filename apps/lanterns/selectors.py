"""Read-only lanterns queries."""

from .models import Lantern


def get_active_lantern(lantern_id):
    """삭제되지 않은 등불만 반환, 없으면 None."""
    return Lantern.objects.filter(pk=lantern_id, deleted_at__isnull=True).first()
