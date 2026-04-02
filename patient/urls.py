from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import PatientProfileViewSet, PatientUserOnboardingView

router = SimpleRouter()
router.register(
    "patient-profiles",
    PatientProfileViewSet,
    basename="admin-patient-profile",
)

urlpatterns = [
    path(
        "patient-users/",
        PatientUserOnboardingView.as_view(),
        name="admin-patient-user-onboarding",
    ),
    path("", include(router.urls)),
]
