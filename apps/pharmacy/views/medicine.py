from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from ..models import Medicine
from ..serializers import MedicineSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["medicines"])
class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.select_related("category", "supplier")
    serializer_class = MedicineSerializer
    permission_classes = [AllowAny]
