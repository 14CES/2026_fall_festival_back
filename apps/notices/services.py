"""Notices business logic and write operations."""

from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.notices.models import Notice


@transaction.atomic
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


@transaction.atomic
def update_notice(
    notice: Notice,
    *,
    title: str,
    content: str,
    type: str = Notice.Type.NORMAL,
    image_url: str | None = None,
) -> Notice:
    """기존 공지사항을 수정하고 수정 일시를 갱신합니다."""
    notice.title = title
    notice.content = content
    notice.type = type
    notice.image_url = image_url
    notice.updated_at = timezone.now()
    notice.save(update_fields=["title", "content", "type", "image_url", "updated_at"])
    return notice


@transaction.atomic
def delete_notice(notice: Notice) -> None:
    """공지사항을 논리 삭제(Soft Delete) 처리합니다."""
    notice.deleted_at = timezone.now()
    notice.save(update_fields=["deleted_at", "updated_at"])

