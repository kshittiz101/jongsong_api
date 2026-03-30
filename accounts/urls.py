from django.urls import path
from .views import (
    AdminRegistrationBySuperuserView,
    PublicUserRegistrationView,
    StaffRegistrationBySuperuserView,
    LoginView,
    RefreshView,
    LogoutView,
)

urlpatterns = [
    path("register/", PublicUserRegistrationView.as_view(), name="public-register"),
    path("admin/register/", AdminRegistrationBySuperuserView.as_view(), name="admin-register"),
    path("staff/register/", StaffRegistrationBySuperuserView.as_view(), name="staff-register"),

    # login
    path("login/", LoginView.as_view(), name="jwt-login"),
    path("refresh-token/", RefreshView.as_view(), name="jwt-refresh"),
    path("logout/", LogoutView.as_view(), name="jwt-logout"),
]