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

