"""Authorization helpers for home-care clinical APIs."""

from __future__ import annotations

from typing import Optional, Set

from django.contrib.auth import get_user_model

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
    if not user.is_authenticated:
        return set()
    if is_homecare_admin(user):
        return None
    ids: Set[int] = set()
    if hasattr(user, "patient_profile"):
        ids.add(user.id)
    return ids


def can_manage_homecare_patient(actor, patient_user: User) -> bool:
    """Whether actor may create/update clinical rows for this patient user."""
    if not actor.is_authenticated:
        return False
    if is_homecare_admin(actor):
        return True
    if patient_user.id == actor.id and hasattr(actor, "patient_profile"):
        return True
    return False
