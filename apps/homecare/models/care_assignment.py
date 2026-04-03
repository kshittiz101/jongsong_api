from django.core.exceptions import ValidationError
from django.db import models

from apps.accounts.models import CustomUser


class PatientCareAssignment(models.Model):
    """Home-care team assignment; at most one active row per patient."""

    patient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="care_assignments",
    )
    doctor = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doctor_care_assignments",
    )
    nurse = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="nurse_care_assignments",
    )
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-assigned_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=("patient",),
                condition=models.Q(is_active=True),
                name="homecare_unique_active_care_assignment",
            ),
        ]

    def clean(self):
        if self.doctor_id and self.nurse_id and self.doctor_id == self.nurse_id:
            raise ValidationError(
                {"nurse": "Doctor and nurse must be different users."}
            )

    def __str__(self):
        return f"Care assignment patient={self.patient_id} active={self.is_active}"
