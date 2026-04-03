from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from ..permissions import HomeCareClinicalPermission
from ..selectors import filter_by_optional_patient_param, get_medication_reports_queryset
from ..serializers import MedicationReportSerializer

_TAG = ["home care"]


@extend_schema_view(**{a: extend_schema(tags=_TAG) for a in ("list", "retrieve", "create", "update", "partial_update", "destroy")})
class MedicationReportViewSet(viewsets.ModelViewSet):
    permission_classes = [HomeCareClinicalPermission]
    serializer_class = MedicationReportSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ("report_date", "id")
    ordering = ("-report_date",)

    def get_queryset(self):
        user = self.request.user
        qs = get_medication_reports_queryset(user)
        return filter_by_optional_patient_param(qs, self.request, user, "patient_id")
