"""Shared validation for clinical rows scoped to a patient user."""

from __future__ import annotations

from rest_framework import serializers

from ..access import can_edit_homecare_patient


def require_homecare_patient_actor(
    request,
    patient_user,
    *,
    denied_message: str = "You are not allowed to manage data for this patient.",
):
    """
    Ensure the request user may create or bind home-care clinical data for ``patient_user``.
    Returns ``patient_user`` on success.
    """
    if not request or not request.user.is_authenticated:
        raise serializers.ValidationError("Authentication required.")
    if not can_edit_homecare_patient(request.user, patient_user):
        raise serializers.ValidationError(denied_message)
    return patient_user
