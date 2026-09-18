"""Admins database models."""

from django.db import models

from common.models import SoftDeleteModel


class Admin(SoftDeleteModel):
    """Admin model for festival managers."""

    admin_key = models.CharField(max_length=255, help_text="관리자 키(해시 저장) / 관리자 인증")
    name = models.CharField(max_length=30, null=True, blank=True, help_text="관리자 구분명")
    last_login_at = models.DateTimeField(null=True, blank=True, help_text="마지막 접속 시각")

    class Meta:
        db_table = "admin"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name or f"Admin({self.pk})"
