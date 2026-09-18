"""Notices database models."""

from django.db import models

from common.models import SoftDeleteModel


class Notice(SoftDeleteModel):
    """Notice model for festival announcements."""

    class Type(models.TextChoices):
        URGENT = "URGENT", "긴급"
        NORMAL = "NORMAL", "일반"

    admin = models.ForeignKey(
        "admins.Admin",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notices",
        help_text="작성 관리자",
    )
    type = models.CharField(
        max_length=10,
        choices=Type.choices,
        default=Type.NORMAL,
        help_text="공지 유형 (URGENT: 긴급, NORMAL: 일반)",
    )
    title = models.CharField(max_length=200, help_text="공지 제목")
    content = models.TextField(help_text="공지 본문")
    image_url = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="첨부 사진 URL",
    )

    class Meta:
        db_table = "notice"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_type_display()}] {self.title}"
