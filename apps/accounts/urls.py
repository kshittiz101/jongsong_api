from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    AdminRegistrationBySuperuserView,
    CurrentUserView,
    DesignationDetailView,
    DesignationListCreateView,
    LoginView,
    LogoutView,
    PatientProfileMeView,
    PatientProfileViewSet,
    PatientUserOnboardingView,
    PublicUserRegistrationView,
    RefreshView,
    StaffManagementViewSet,
    StaffRegistrationBySuperuserView,
    UserDetailView,
    UserListView,
)

_staff_router = SimpleRouter()
_staff_router.register(
    "admin/staff",
    StaffManagementViewSet,
    basename="admin-staff",
)

_patient_router = SimpleRouter()
_patient_router.register(
    "admin/patient-profiles",
    PatientProfileViewSet,
    basename="admin-patient-profile",
)

# Mounted at /api/auth/ via core.default_routers → accounts.urls.
# Order matches jongsong-ui ApiActions auth block for easy cross-reference.
user_urlpatterns = [
    path("public-user/", PublicUserRegistrationView.as_view(), name="public-register"),
    path("admin-user/", AdminRegistrationBySuperuserView.as_view(), name="admin-register"),
    path("staff-user/", StaffRegistrationBySuperuserView.as_view(), name="staff-register"),
    path("login/", LoginView.as_view(), name="login"),
    path("authenticate-user/", CurrentUserView.as_view(), name="authenticate-user"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

urlpatterns = [
    path("users/<int:pk>/", UserDetailView.as_view(), name="users-detail"),
    path("users/", UserListView.as_view(), name="users-list"),
    path(
        "admin/designations/",
        DesignationListCreateView.as_view(),
        name="admin-designations-list",
    ),
    path(
        "admin/designations/<int:pk>/",
        DesignationDetailView.as_view(),
        name="admin-designations-detail",
    ),
    path("auth/", include(user_urlpatterns)),
    path(
        "admin/patient-users/",
        PatientUserOnboardingView.as_view(),
        name="admin-patient-user-onboarding",
    ),
    path(
        "patient-profiles/me/",
        PatientProfileMeView.as_view(),
        name="patient-profile-me",
    ),
    path("", include(_staff_router.urls)),
    path("", include(_patient_router.urls)),
]