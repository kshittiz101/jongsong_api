from drf_spectacular.utils import extend_schema_view
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from ..permissions import HomeCareClinicalPermission
from ..selectors import (
    filter_by_optional_patient_param,
    get_medication_logs_queryset,
    get_medications_queryset,
)
from ..serializers import MedicationLogSerializer, MedicationSerializer

from .schema import HOMECARE_CLINICAL_SCHEMA


@extend_schema_view(**HOMECARE_CLINICAL_SCHEMA)
class HomeCareMedicationViewSet(viewsets.ModelViewSet):
    permission_classes = [HomeCareClinicalPermission]
    serializer_class = MedicationSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ("created_at", "id")
    ordering = ("-created_at",)

    def get_queryset(self):
        user = self.request.user
        qs = get_medications_queryset(user)
        return filter_by_optional_patient_param(qs, self.request, user, "patient_id")


@extend_schema_view(**HOMECARE_CLINICAL_SCHEMA)
class MedicationLogViewSet(viewsets.ModelViewSet):
    permission_classes = [HomeCareClinicalPermission]
    serializer_class = MedicationLogSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ("scheduled_time", "id")
    ordering = ("-scheduled_time",)

    def get_queryset(self):
        user = self.request.user
        qs = get_medication_logs_queryset(user)
        qs = filter_by_optional_patient_param(
            qs, self.request, user, "medication__patient_id"
        )
        med_id = self.request.query_params.get("medication")
        if med_id:
            try:
                qs = qs.filter(medication_id=int(med_id))
            except (TypeError, ValueError):
                return qs.none()
        return qs
