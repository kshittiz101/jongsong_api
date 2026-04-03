from rest_framework import status
from rest_framework.response import Response


class SuccessResponseMixin:
    """Wraps responses in a consistent success envelope."""

    def success_response(self, data=None, status_code=status.HTTP_200_OK, **kwargs):
        payload = {"success": True, "data": data or {}}
        payload.update(kwargs)
        return Response(payload, status=status_code)

    def created_response(self, data):
        return self.success_response(data, status_code=status.HTTP_201_CREATED)
