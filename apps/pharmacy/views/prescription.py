from rest_framework import viewsets

from ..models import Prescription
from ..permissions import PrescriptionStatusPermission
from ..serializers import PrescriptionSerializer
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["prescriptions"])
class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [PrescriptionStatusPermission]
