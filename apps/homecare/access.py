"""Authorization helpers for home-care clinical APIs."""

from __future__ import annotations

from typing import Optional, Set

from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


def is_homecare_admin(user) -> bool:
    return bool(
        user
        and user.is_authenticated
        and (user.is_superuser or hasattr(user, "admin_profile"))
    )


def homecare_visible_patient_ids(user) -> Optional[Set[int]]:
    """
    Patient user-ids the actor may access for clinical home-care data.
    Returns None if unrestricted (platform admin).
    """
    from .models import PatientCareAssignment

    if not user.is_authenticated:
        return set()
    if is_homecare_admin(user):
        return None
    ids: Set[int] = set()
    if hasattr(user, "patient_profile"):
        ids.add(user.id)
    assigned = PatientCareAssignment.objects.filter(
        is_active=True,
    ).filter(Q(doctor_id=user.id) | Q(nurse_id=user.id)).values_list(
        "patient_id",
        flat=True,
    )
    ids.update(assigned)
    return ids


def can_manage_homecare_patient(actor, patient_user: User) -> bool:
    """Whether actor may create/update clinical rows for this patient user."""
    from .models import PatientCareAssignment

    if not actor.is_authenticated:
        return False
    if is_homecare_admin(actor):
        return True
    if patient_user.id == actor.id and hasattr(actor, "patient_profile"):
        return True
    return PatientCareAssignment.objects.filter(
        is_active=True,
        patient_id=patient_user.id,
    ).filter(Q(doctor_id=actor.id) | Q(nurse_id=actor.id)).exists()


def patient_users_with_profile_queryset():
    return User.objects.filter(patient_profile__isnull=False)
