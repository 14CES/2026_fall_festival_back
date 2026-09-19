"""drf-spectacular helpers for the shared response envelope.

Pure ``APIView`` cannot be introspected by drf-spectacular, so every view
declares its response shape explicitly.
"""

from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer):
    """Failure envelope for Swagger. ``errors`` uses JSONField, not DictField:
    real DRF validation errors can be lists or nested structures
    (e.g. {"size": ["Ensure this value is less than or equal to 100."]}),
    not just flat string values."""

    success = serializers.BooleanField(default=False)
    code = serializers.CharField()
    message = serializers.CharField()
    errors = serializers.JSONField(default=dict)
