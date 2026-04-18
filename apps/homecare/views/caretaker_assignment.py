from drf_spectacular.utils import extend_schema_view
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from ..permissions import HomeCareClinicalPermission
from ..selectors import (
    filter_by_optional_patient_param,
    get_caretaker_assignments_queryset,
)
from ..serializers import PatientCaretakerAssignmentSerializer

from .schema import HOMECARE_ASSIGNMENT_SCHEMA


@extend_schema_view(**HOMECARE_ASSIGNMENT_SCHEMA)
class PatientCaretakerAssignmentViewSet(viewsets.ModelViewSet):
    """
    Home-care caretaker ↔ patient assignments.

    Platform admins see all rows; patients and assigned home-care staff only
    see assignments for patients they are allowed to view (see
    ``homecare_visible_patient_ids``).
    """

    permission_classes = [HomeCareClinicalPermission]
    serializer_class = PatientCaretakerAssignmentSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ("assigned_at", "id")
    ordering = ("-assigned_at",)

    def get_queryset(self):
        user = self.request.user
        qs = get_caretaker_assignments_queryset(user)
        qs = filter_by_optional_patient_param(qs, self.request, user, "patient_id")
        cid = self.request.query_params.get("caretaker")
        if cid is not None:
            try:
                qs = qs.filter(caretaker_id=int(cid))
            except (TypeError, ValueError):
                return qs.none()
        flag = self.request.query_params.get("is_active")
        if flag is not None:
            v = str(flag).strip().lower()
            if v in {"true", "1", "yes"}:
                qs = qs.filter(is_active=True)
            elif v in {"false", "0", "no"}:
                qs = qs.filter(is_active=False)
        return qs
