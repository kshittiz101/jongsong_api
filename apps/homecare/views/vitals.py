from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from ..permissions import HomeCareClinicalPermission
from ..selectors import filter_by_optional_patient_param, get_vitals_queryset
from ..serializers import PatientVitalReadingSerializer

_TAG = ["home care"]


@extend_schema_view(**{a: extend_schema(tags=_TAG) for a in ("list", "retrieve", "create", "update", "partial_update", "destroy")})
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
