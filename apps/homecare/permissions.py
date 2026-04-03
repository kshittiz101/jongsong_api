from rest_framework.permissions import SAFE_METHODS, BasePermission

from .access import can_manage_homecare_patient


def _is_platform_admin(user):
    return bool(
        user
        and user.is_authenticated
        and (user.is_superuser or hasattr(user, "admin_profile"))
    )


class HomeCareClinicalPermission(BasePermission):
    """
    Authenticated users only. Object access if platform admin or allowed to manage
    that patient's home-care clinical data (patient self or assigned doctor/nurse).
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


class PatientCareAssignmentPermission(BasePermission):
    """
    Writes: admin only. Reads: patient (self), assigned doctor, assigned nurse, or admin.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        action = getattr(view, "action", None)
        if action in ("create", "update", "partial_update", "destroy"):
            return _is_platform_admin(request.user)
        return True

    def has_object_permission(self, request, view, obj):
        if _is_platform_admin(request.user):
            return True
        u = request.user
        if obj.patient_id == u.id or obj.doctor_id == u.id or obj.nurse_id == u.id:
            return request.method in SAFE_METHODS
        return False
