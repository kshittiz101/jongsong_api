from rest_framework.permissions import BasePermission


def _is_platform_admin(user):
    return bool(
        user
        and user.is_authenticated
        and (user.is_superuser or hasattr(user, "admin_profile"))
    )


class PatientProfilePermission(BasePermission):
    """
    list/create: admin (or superuser) only.
    retrieve/update/partial_update: admin or owning patient user.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if getattr(view, "action", None) == "me":
            return True
        action = getattr(view, "action", None)
        if action in ("list", "create"):
            return _is_platform_admin(request.user)
        return True

    def has_object_permission(self, request, view, obj):
        if _is_platform_admin(request.user):
            return True
        return obj.user_id == request.user.id
