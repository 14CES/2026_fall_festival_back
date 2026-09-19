"""Notices business logic and write operations."""

from typing import Any

from apps.notices.models import Notice


def create_notice(
    *,
    title: str,
    content: str,
    type: str = Notice.Type.NORMAL,
    image_url: str | None = None,
    admin: Any = None,
) -> Notice:
    """새로운 공지사항을 생성합니다."""
    return Notice.objects.create(
        title=title,
        content=content,
        type=type,
        image_url=image_url,
        admin=admin,
    )
