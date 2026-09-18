"""분실물 상태를 실제로 바꾸는(등록/수정/삭제) 로직"""

from django.db import transaction

from .models import LostItem, LostItemImage, LostItemTag


@transaction.atomic
def create_lost_item(*, title, found_date, image_urls, tags, admin_id=None):
    lost_item = LostItem.objects.create(
        title=title,
        found_date=found_date,
        created_by_admin_id=admin_id,
    )
    LostItemImage.objects.bulk_create(
        LostItemImage(lost_item=lost_item, image_url=url, sort_order=index)
        for index, url in enumerate(image_urls, start=1)
    )
    LostItemTag.objects.bulk_create(
        LostItemTag(lost_item=lost_item, keyword=keyword, sort_order=index)
        for index, keyword in enumerate(tags, start=1)
    )
    return lost_item