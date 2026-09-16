"""Read-only lost items queries.

Every query filters ``deleted_at IS NULL`` on the item *and* on its children,
so soft-deleted images and tags never leak into a response.
"""

from django.db.models import Prefetch

from .models import LostItem, LostItemImage, LostItemTag

LIST_TAG_LIMIT = 3


def _alive_children():
    images = LostItemImage.objects.alive().order_by("sort_order", "image_id")
    tags = LostItemTag.objects.alive().order_by("sort_order", "tag_id")
    return [
        Prefetch("images", queryset=images, to_attr="alive_images"),
        Prefetch("tags", queryset=tags, to_attr="alive_tags"),
    ]


def list_lost_items(*, found_date=None):
    """Admin list queryset, newest first. Caller paginates."""
    queryset = LostItem.objects.alive()
    if found_date is not None:
        queryset = queryset.filter(found_date=found_date)
    return queryset.prefetch_related(*_alive_children()).order_by("-created_at", "-lost_item_id")


def get_lost_item(lost_item_id):
    """Return a live lost item with its live children, or ``None``."""
    return (
        LostItem.objects.alive()
        .prefetch_related(*_alive_children())
        .filter(pk=lost_item_id)
        .first()
    )


def thumbnail_url(lost_item):
    images = getattr(lost_item, "alive_images", None)
    return images[0].image_url if images else None


def top_keywords(lost_item, limit=LIST_TAG_LIMIT):
    tags = getattr(lost_item, "alive_tags", []) or []
    return [tag.keyword for tag in tags[:limit]]