from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from ..permissions import PatientCareAssignmentPermission
from ..selectors import get_care_assignments_queryset
from ..serializers import PatientCareAssignmentSerializer

_TAG = ["home care"]


@extend_schema_view(**{a: extend_schema(tags=_TAG) for a in ("list", "retrieve", "create", "update", "partial_update", "destroy")})
class PatientCareAssignmentViewSet(viewsets.ModelViewSet):
    permission_classes = [PatientCareAssignmentPermission]
    serializer_class = PatientCareAssignmentSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ("assigned_at", "id")
    ordering = ("-assigned_at",)

    def get_queryset(self):
        return get_care_assignments_queryset(self.request.user)
