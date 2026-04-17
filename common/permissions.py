from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.is_superuser)


class IsAdminOrSuperUser(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or hasattr(user, "admin_profile"))
        )


class IsDashboardStaffOrAdmin(BasePermission):
    """
    Matches jongsong-ui dashboard gate: superuser, Django staff flag, admin profile,
    or staff profile (home care / clinical staff).
    """

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        return bool(
            user.is_superuser
            or user.is_staff
            or hasattr(user, "admin_profile")
            or hasattr(user, "staff_profile")
        )

