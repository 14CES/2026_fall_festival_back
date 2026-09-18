"""Lanterns database models."""

from django.db import models
from django.utils import timezone


class Lantern(models.Model):
    class DeletedBy(models.TextChoices):
        USER = "USER", "사용자"
        ADMIN = "ADMIN", "관리자"

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="lanterns")
    booth = models.ForeignKey("booths.Booth", on_delete=models.CASCADE, related_name="lanterns")
    nickname = models.CharField(max_length=10, default="익명의 코끼리")
    message = models.CharField(max_length=30)
    festival_date = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    deleted_by = models.CharField(max_length=10, choices=DeletedBy.choices, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "booth", "festival_date"], name="unique_user_booth_lantern_per_day"
            )
        ]
        indexes = [
            models.Index(fields=["user", "festival_date"], name="idx_lantern_user_date"),
            models.Index(fields=["booth", "deleted_at"], name="idx_lantern_booth_deleted"),
        ]

    def __str__(self):
        return f"Lantern #{self.id} (user={self.user_id}, booth={self.booth_id})"


class LanternReport(models.Model):
    class Reason(models.TextChoices):
        ABUSE = "ABUSE", "욕설 및 비방"
        FALSE_INFO = "FALSE_INFO", "허위정보"
        OBSCENE = "OBSCENE", "음란·불쾌"
        ETC = "ETC", "기타"

    id = models.BigAutoField(primary_key=True)
    lantern = models.ForeignKey(Lantern, on_delete=models.CASCADE, related_name="lantern_reports")
    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="lantern_reports"
    )
    reason = models.CharField(max_length=20, choices=Reason.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["lantern", "user"], name="unique_lantern_user_report")
        ]

    def __str__(self):
        return f"Report #{self.id} (lantern={self.lantern_id}, reason={self.reason})"
