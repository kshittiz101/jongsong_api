"""
Homecare services — business logic layer.

Complex orchestration (e.g. activating a new care assignment while
deactivating the previous one) lives here so views remain thin.
"""
from __future__ import annotations

import logging

from django.db import transaction
from django.utils import timezone

from .models import PatientCareAssignment

logger = logging.getLogger(__name__)


class CareAssignmentService:
    @staticmethod
    @transaction.atomic
    def activate_assignment(assignment: PatientCareAssignment) -> PatientCareAssignment:
        """
        Activate a care assignment, deactivating any previously active
        assignment for the same patient.
        """
        PatientCareAssignment.objects.filter(
            patient_id=assignment.patient_id,
            is_active=True,
        ).exclude(pk=assignment.pk).update(
            is_active=False,
            ended_at=timezone.now(),
        )
        assignment.is_active = True
        assignment.save(update_fields=["is_active"])
        logger.info(
            "Care assignment activated",
            extra={"assignment_id": assignment.pk, "patient_id": assignment.patient_id},
        )
        return assignment
