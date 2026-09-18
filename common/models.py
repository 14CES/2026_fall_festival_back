"""공통 Soft Delete 모델."""

from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """삭제되지 않은 데이터 조회 및 Soft Delete 기능."""

    def alive(self):
        # 삭제되지 않은 데이터만 조회
        return self.filter(deleted_at__isnull=True)

    def soft_delete(self, deleted_at=None):
        # 실제 삭제 대신 deleted_at에 삭제 시각 저장
        return self.update(deleted_at=deleted_at or timezone.now())


class SoftDeleteModel(models.Model):
    """생성, 수정, 삭제 시각을 공통으로 관리하는 모델."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteQuerySet.as_manager()

    class Meta:
        abstract = True
