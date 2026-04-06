from rest_framework import viewsets

from ..models import Prescription
from ..permissions import PrescriptionStatusPermission
from ..serializers import PrescriptionSerializer


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [PrescriptionStatusPermission]
