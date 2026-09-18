"""Shared pagination primitives.

``page`` is 0-based and ``size`` is capped, per the API 명세서. Bounds are
validated once, in ``LostItemListQuerySerializer`` — this module trusts the
values it's given rather than re-clamping them.
"""

from dataclasses import dataclass

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


@dataclass(frozen=True)
class Page:
    items: list
    total_count: int
    page: int
    size: int

    @property
    def has_next(self) -> bool:
        return (self.page + 1) * self.size < self.total_count

    def as_meta(self) -> dict:
        return {
            "total_count": self.total_count,
            "page": self.page,
            "size": self.size,
            "has_next": self.has_next,
        }


def paginate(queryset, page, size) -> Page:
    offset = page * size
    return Page(list(queryset[offset : offset + size]), queryset.count(), page, size)