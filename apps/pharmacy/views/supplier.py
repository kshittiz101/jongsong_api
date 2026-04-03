from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from ..models import Supplier
from ..serializers import SupplierSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [AllowAny]
