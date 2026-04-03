"""
Homecare selectors — query builders that keep views thin.

All queryset construction and filtering logic lives here; views simply
call these functions and pass the resulting queryset to serializers.
"""
from __future__ import annotations

from django.db.models import QuerySet

from .access import homecare_visible_patient_ids, is_homecare_admin
from .models import (
    Medication,
    MedicationLog,
    MedicationReport,
    PatientCareAssignment,
    PatientVitalReading,
)


def filter_by_visible_patients(qs: QuerySet, user, patient_field: str = "patient_id") -> QuerySet:
    """Restrict queryset to patients the actor is allowed to see."""
    ids = homecare_visible_patient_ids(user)
    if ids is not None:
        return qs.filter(**{f"{patient_field}__in": ids})
    return qs


def filter_by_optional_patient_param(
    qs: QuerySet,
    request,
    user,
    patient_field: str = "patient_id",
) -> QuerySet:
    """
    Further filter by the ?patient=<pk> query param when provided.
    Returns qs.none() on an invalid or unauthorized patient value.
    """
    raw = request.query_params.get("patient")
    if not raw:
        return qs
    try:
        pid = int(raw)
    except (TypeError, ValueError):
        return qs.none()

    if is_homecare_admin(user):
        return qs.filter(**{patient_field: pid})

    visible = homecare_visible_patient_ids(user)
    if visible is not None and pid in visible:
        return qs.filter(**{patient_field: pid})
    return qs.none()


def get_vitals_queryset(user) -> QuerySet:
    qs = PatientVitalReading.objects.select_related("patient", "recorded_by")
    qs = filter_by_visible_patients(qs, user, "patient_id")
    return qs


def get_medications_queryset(user) -> QuerySet:
    qs = Medication.objects.select_related("patient")
    qs = filter_by_visible_patients(qs, user, "patient_id")
    return qs


def get_medication_logs_queryset(user) -> QuerySet:
    return (
        MedicationLog.objects
        .select_related("medication", "medication__patient", "marked_by")
        .filter(
            **{"medication__patient_id__in": homecare_visible_patient_ids(user)}
        )
        if homecare_visible_patient_ids(user) is not None
        else MedicationLog.objects.select_related(
            "medication", "medication__patient", "marked_by"
        )
    )


def get_medication_reports_queryset(user) -> QuerySet:
    qs = MedicationReport.objects.select_related("patient", "recorded_by")
    qs = filter_by_visible_patients(qs, user, "patient_id")
    return qs


def get_care_assignments_queryset(user) -> QuerySet:
    from django.db.models import Q

    qs = PatientCareAssignment.objects.select_related("patient", "doctor", "nurse")
    if is_homecare_admin(user):
        return qs
    return qs.filter(
        Q(patient_id=user.id) | Q(doctor_id=user.id) | Q(nurse_id=user.id)
    )
