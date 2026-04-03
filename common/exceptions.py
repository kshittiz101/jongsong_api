import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Global DRF exception handler.

    Wraps all error responses in a consistent envelope:
        { "success": false, "status_code": ..., "errors": ... }
    Unhandled exceptions are logged and returned as 500.
    """
    response = exception_handler(exc, context)

    if response is not None:
        view = context.get("view", None)
        logger.warning(
            "API exception",
            extra={
                "exc_type": type(exc).__name__,
                "view": view.__class__.__name__ if view else None,
                "status_code": response.status_code,
            },
        )
        response.data = {
            "success": False,
            "status_code": response.status_code,
            "errors": response.data,
        }
    else:
        logger.error("Unhandled exception", exc_info=exc)
        response = Response(
            {"success": False, "status_code": 500, "errors": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
