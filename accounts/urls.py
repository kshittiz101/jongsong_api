from django.urls import include, path

from .views import (
    AdminRegistrationBySuperuserView,
    CurrentUserView,
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
    path("me/", CurrentUserView.as_view(), name="current-user"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

urlpatterns = [
    path("auth/", include(user_urlpatterns)),
]