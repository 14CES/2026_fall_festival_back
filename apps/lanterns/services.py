"""Transactional lanterns state changes."""

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.booths.models import Booth
from apps.lanterns.models import Lantern


@transaction.atomic
def delete_admin_lantern(lantern: Lantern) -> None:
    """관리자가 부적절한 등불을 블라인드(Soft Delete) 처리하고,
    연관된 부스의 등불 카운트를 1 차감합니다.
    """
    lantern.deleted_at = timezone.now()
    lantern.deleted_by = Lantern.DeletedBy.ADMIN
    lantern.save(update_fields=["deleted_at", "deleted_by", "updated_at"])

    Booth.objects.filter(id=lantern.booth_id, lantern_count__gt=0).update(
        lantern_count=F("lantern_count") - 1
    )
