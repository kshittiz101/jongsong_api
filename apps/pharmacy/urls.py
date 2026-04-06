from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SupplierViewSet,
    CategoryViewSet,
    MedicineViewSet,
    PrescriptionViewSet,
)

router = DefaultRouter()
router.register(r"suppliers", SupplierViewSet, basename="supplier")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"medicines", MedicineViewSet, basename="medicine")
router.register(r"prescriptions", PrescriptionViewSet, basename="prescription")

urlpatterns = [
    path("", include(router.urls)),
]
