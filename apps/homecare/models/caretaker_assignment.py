from django.core.exceptions import ValidationError
from django.db import models

from apps.accounts.models import CustomUser
from common.constants.patient_types import PatientType
from common.constants.roles import Role


class PatientCaretakerAssignment(models.Model):
    """Links a home-care patient to a staff caretaker who may manage clinical data."""

    patient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="caretaker_assignments",
    )
    caretaker = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="patient_caretaker_assignments",
    )
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    assigned_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="caretaker_assignments_created",
    )

    class Meta:
        ordering = ["-assigned_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["patient", "caretaker"],
                condition=models.Q(is_active=True),
                name="uniq_active_homecare_patient_caretaker",
            )
        ]

    def __str__(self):
        return f"{self.caretaker_id} → patient {self.patient_id} (active={self.is_active})"

    def clean(self):
        super().clean()
        if self.patient_id and self.caretaker_id and self.patient_id == self.caretaker_id:
            raise ValidationError("Caretaker cannot be the same user as the patient.")
        patient = self.patient
        if patient and not hasattr(patient, "patient_profile"):
            raise ValidationError({"patient": "User must have a patient profile."})
        if patient and hasattr(patient, "patient_profile"):
            if patient.patient_profile.patient_type != PatientType.HOME_CARE:
                raise ValidationError(
                    {"patient": "Patient must be a home-care patient."}
                )
        caretaker = self.caretaker
        if caretaker and hasattr(caretaker, "patient_profile"):
            raise ValidationError(
                {"caretaker": "Caretaker must not have a patient profile."}
            )
        staff = getattr(caretaker, "staff_profile", None) if caretaker else None
        if caretaker and (not staff or staff.role != Role.HOME_CARE_STAFF):
            raise ValidationError(
                {"caretaker": "Caretaker must be home-care staff."}
            )
