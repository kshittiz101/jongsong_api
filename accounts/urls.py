from django.urls import include, path

from .views import (
    AdminRegistrationBySuperuserView,
    CurrentUserView,
    DesignationDetailView,
    DesignationListCreateView,
    LoginView,
    LogoutView,
    PublicUserRegistrationView,
    RefreshView,
    StaffRegistrationBySuperuserView,
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
    path("register/", PublicUserRegistrationView.as_view(), name="public-register-legacy"),
    path("admin/register/", AdminRegistrationBySuperuserView.as_view(), name="admin-register-legacy"),
    path("staff/register/", StaffRegistrationBySuperuserView.as_view(), name="staff-register-legacy"),
]