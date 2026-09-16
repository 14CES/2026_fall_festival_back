"""Shared model primitives.

Soft delete is expressed as ``deleted_at``. Live rows always satisfy
``deleted_at IS NULL``; every selector in the project relies on that invariant.
"""

from django.db import models


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet that knows how to hide soft-deleted rows.

    Only ``alive()`` is needed right now — the read-only lost-items API never
    deletes anything. A ``soft_delete()`` bulk helper can be added here once
    the delete endpoint lands, instead of carrying unused code today.
    """

    def alive(self):
        return self.filter(deleted_at__isnull=True)


class SoftDeleteModel(models.Model):
    """Abstract base with creation/update/soft-delete timestamps.

    ``updated_at`` stays NULL until the row is actually modified, because the API
    spec returns ``updated_at: null`` for records that were never edited.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteQuerySet.as_manager()

    class Meta:
        abstract = True