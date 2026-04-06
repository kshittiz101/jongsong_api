from rest_framework.permissions import BasePermission


def is_superuser_or_pharmacist(user):
    """
    Check if user is superuser or a staff with Pharmacist designation.
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True

    # Check if user has staff_profile with Pharmacist designation
    staff_profile = getattr(user, "staff_profile", None)
    if staff_profile is None:
        return False

    designation = getattr(staff_profile, "designation", None)
    if designation is None:
        return False

    return designation.name.lower() == "pharmacist"


class PrescriptionStatusPermission(BasePermission):
    """
    Permission for prescription status updates.
    - Create/List/Retrieve/Destroy: Any user (including unauthenticated)
    - Status update: Only superuser or staff with 'Pharmacist' designation
    """

    def has_permission(self, request, view):
        # Allow all users including unauthenticated for basic CRUD
        return True

    def has_object_permission(self, request, view, obj):
        action = getattr(view, "action", None)

        # For partial_update, check if status is being changed
        if action == "partial_update":
            if "status" in request.data:
                return is_superuser_or_pharmacist(request.user)
            return True

        # For full update, check if status field is included
        if action == "update":
            if "status" in request.data:
                return is_superuser_or_pharmacist(request.user)
            return True

        return True
