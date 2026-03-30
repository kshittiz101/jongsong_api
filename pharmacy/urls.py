from django.urls import path, include
from rest_framework.routers import DefaultRouter
from pharmacy.views import SupplierViewSet, CategoryViewSet, MedicineViewSet

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'medicines', MedicineViewSet, basename='medicine')

urlpatterns = [
    path('', include(router.urls)),
]