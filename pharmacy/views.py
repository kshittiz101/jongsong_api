from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from pharmacy.models import Supplier, Category, Medicine
from pharmacy.serializers import (
    SupplierSerializer,
    CategorySerializer,
    MedicineSerializer,
)

# Create your views here.
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [AllowAny]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.select_related("category", "supplier")
    serializer_class = MedicineSerializer
    permission_classes = [AllowAny]