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
    PatientCaretakerAssignment,
    PatientDailyClinicalReport,
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
    qs = MedicationLog.objects.select_related(
        "medication", "medication__patient", "marked_by"
    )
    visible = homecare_visible_patient_ids(user)
    if visible is not None:
        qs = qs.filter(medication__patient_id__in=visible)
    return qs


def get_medication_reports_queryset(user) -> QuerySet:
    qs = MedicationReport.objects.select_related("patient", "recorded_by")
    qs = filter_by_visible_patients(qs, user, "patient_id")
    return qs


def get_daily_clinical_reports_queryset(user) -> QuerySet:
    qs = PatientDailyClinicalReport.objects.select_related("patient")
    qs = filter_by_visible_patients(qs, user, "patient_id")
    return qs


def get_caretaker_assignments_queryset(user) -> QuerySet:
    qs = PatientCaretakerAssignment.objects.select_related(
        "patient", "caretaker", "assigned_by"
    )
    return filter_by_visible_patients(qs, user, "patient_id")
