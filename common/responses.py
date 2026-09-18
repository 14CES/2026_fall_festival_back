"""Shared response helpers.

Every endpoint answers with the same envelope:

    success: {"success": true,  "code": ..., "message": ..., "data": {...}}
    failure: {"success": false, "code": ..., "message": ..., "errors": {...}}
"""

from rest_framework import status as http_status
from rest_framework.response import Response


def success_response(code, message, data=None, status=http_status.HTTP_200_OK):
    return Response(
        {
            "success": True,
            "code": code,
            "message": message,
            "data": data if data is not None else {},
        },
        status=status,
    )


def error_response(code, message, errors=None, status=http_status.HTTP_400_BAD_REQUEST):
    return Response(
        {"success": False, "code": code, "message": message, "errors": errors or {}},
        status=status,
    )
