from rest_framework.permissions import SAFE_METHODS, BasePermission

from .access import can_edit_homecare_patient, can_view_homecare_patient, is_homecare_admin


class HomeCareClinicalPermission(BasePermission):
    """
    Authenticated users only. Safe methods allowed if the user can view the
    patient; unsafe methods require edit rights (admin or assigned caretaker).
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if is_homecare_admin(request.user):
            return True
        patient_user = getattr(obj, "patient", None)
        if patient_user is None and hasattr(obj, "medication"):
            med = obj.medication
            patient_user = getattr(med, "patient", None) if med else None
        if patient_user is None:
            return False
        if request.method in SAFE_METHODS:
            return can_view_homecare_patient(request.user, patient_user)
        return can_edit_homecare_patient(request.user, patient_user)
