from django.urls import include, path
from rest_framework.routers import SimpleRouter

from staff.views import StaffManagementViewSet


router = SimpleRouter()
router.register("admin/staff", StaffManagementViewSet, basename="admin-staff")

urlpatterns = [
    path("", include(router.urls)),
]
