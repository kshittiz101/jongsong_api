from rest_framework.permissions import BasePermission

from .access import can_manage_homecare_patient


def _is_platform_admin(user):
    return bool(
        user
        and user.is_authenticated
        and (user.is_superuser or hasattr(user, "admin_profile"))
    )


class HomeCareClinicalPermission(BasePermission):
    """
    Authenticated users only. Object access if platform admin or the patient
    managing their own home-care clinical data.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if _is_platform_admin(request.user):
            return True
        patient_user = getattr(obj, "patient", None)
        if patient_user is None and hasattr(obj, "medication"):
            med = obj.medication
            patient_user = getattr(med, "patient", None) if med else None
        if patient_user is None:
            return False
        return can_manage_homecare_patient(request.user, patient_user)
