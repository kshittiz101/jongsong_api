from drf_spectacular.utils import extend_schema_view
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsAdminOrSuperUser

from ..models import PatientCaretakerAssignment
from ..serializers import PatientCaretakerAssignmentSerializer

from .schema import HOMECARE_ASSIGNMENT_SCHEMA


@extend_schema_view(**HOMECARE_ASSIGNMENT_SCHEMA)
class PatientCaretakerAssignmentViewSet(viewsets.ModelViewSet):
    """
    Platform-admin-only API for assigning home-care staff to patients.
    """

    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    serializer_class = PatientCaretakerAssignmentSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ("assigned_at", "id")
    ordering = ("-assigned_at",)

    def get_queryset(self):
        qs = PatientCaretakerAssignment.objects.select_related(
            "patient", "caretaker", "assigned_by"
        )
        pid = self.request.query_params.get("patient")
        if pid is not None:
            try:
                qs = qs.filter(patient_id=int(pid))
            except (TypeError, ValueError):
                return qs.none()
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
