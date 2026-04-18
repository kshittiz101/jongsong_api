from drf_spectacular.utils import extend_schema_view
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from ..permissions import HomeCareClinicalPermission
from ..selectors import filter_by_optional_patient_param, get_vitals_queryset
from ..serializers import PatientVitalReadingSerializer

from .schema import HOMECARE_CLINICAL_SCHEMA


@extend_schema_view(**HOMECARE_CLINICAL_SCHEMA)
class PatientVitalReadingViewSet(viewsets.ModelViewSet):
    permission_classes = [HomeCareClinicalPermission]
    serializer_class = PatientVitalReadingSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ("recorded_at", "id")
    ordering = ("-recorded_at",)

    def get_queryset(self):
        user = self.request.user
        qs = get_vitals_queryset(user)
        return filter_by_optional_patient_param(qs, self.request, user, "patient_id")
