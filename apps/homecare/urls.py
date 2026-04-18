from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    HomeCareMedicationViewSet,
    MedicationLogViewSet,
    MedicationReportViewSet,
    PatientCaretakerAssignmentViewSet,
    PatientDailyClinicalReportViewSet,
    PatientVitalReadingViewSet,
)

router = SimpleRouter()
router.register(
    "admin/home-care/caretaker-assignments",
    PatientCaretakerAssignmentViewSet,
    basename="homecare-caretaker-assignment",
)
router.register(
    "admin/home-care/vitals",
    PatientVitalReadingViewSet,
    basename="homecare-vital",
)
router.register(
    "admin/home-care/medications",
    HomeCareMedicationViewSet,
    basename="homecare-medication",
)
router.register(
    "admin/home-care/medication-logs",
    MedicationLogViewSet,
    basename="homecare-medication-log",
)
router.register(
    "admin/home-care/medication-reports",
    MedicationReportViewSet,
    basename="homecare-medication-report",
)
router.register(
    "admin/home-care/daily-clinical-reports",
    PatientDailyClinicalReportViewSet,
    basename="homecare-daily-clinical-report",
)

urlpatterns = [
    path("", include(router.urls)),
]
