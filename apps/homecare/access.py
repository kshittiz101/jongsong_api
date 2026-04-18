"""Authorization helpers for home-care clinical APIs."""

from __future__ import annotations

from typing import Optional, Set

from django.contrib.auth import get_user_model

from common.constants.roles import Role

User = get_user_model()


def is_homecare_admin(user) -> bool:
    return bool(
        user
        and user.is_authenticated
        and (user.is_superuser or hasattr(user, "admin_profile"))
    )


def is_homecare_caretaker_staff(user) -> bool:
    """Staff user eligible to act as a home-care caretaker when assigned."""
    if not user or not user.is_authenticated:
        return False
    staff = getattr(user, "staff_profile", None)
    return bool(staff and staff.role == Role.HOME_CARE_STAFF)


def caretaker_assigned_patient_ids(user) -> Set[int]:
    """Patient user-ids this caretaker may access (active assignments only)."""
    from .models import PatientCaretakerAssignment

    if not user.is_authenticated:
        return set()
    return set(
        PatientCaretakerAssignment.objects.filter(
            caretaker_id=user.id, is_active=True
        ).values_list("patient_id", flat=True)
    )


def homecare_visible_patient_ids(user) -> Optional[Set[int]]:
    """
    Patient user-ids the actor may access for clinical home-care data.
    Returns None if unrestricted (platform admin).
    """
    if not user.is_authenticated:
        return set()
    if is_homecare_admin(user):
        return None
    ids: Set[int] = set()
    if hasattr(user, "patient_profile"):
        ids.add(user.id)
    if is_homecare_caretaker_staff(user):
        ids.update(caretaker_assigned_patient_ids(user))
    return ids


def _active_caretaker_assignment_exists(actor, patient_user: User) -> bool:
    from .models import PatientCaretakerAssignment

    return PatientCaretakerAssignment.objects.filter(
        caretaker_id=actor.id,
        patient_id=patient_user.id,
        is_active=True,
    ).exists()


def can_view_homecare_patient(actor, patient_user: User) -> bool:
    """Whether actor may read clinical home-care data for this patient user."""
    if not actor.is_authenticated:
        return False
    if is_homecare_admin(actor):
        return True
    if patient_user.id == actor.id and hasattr(actor, "patient_profile"):
        return True
    if is_homecare_caretaker_staff(actor) and _active_caretaker_assignment_exists(
        actor, patient_user
    ):
        return True
    return False


def can_edit_homecare_patient(actor, patient_user: User) -> bool:
    """Whether actor may create/update/delete clinical rows for this patient (not the patient themselves)."""
    if not actor.is_authenticated:
        return False
    if is_homecare_admin(actor):
        return True
    if patient_user.id == actor.id:
        return False
    if is_homecare_caretaker_staff(actor) and _active_caretaker_assignment_exists(
        actor, patient_user
    ):
        return True
    return False
