from django.db import models

from apps.accounts.models import CustomUser


class MedicationReport(models.Model):
    """Narrative daily medication report from caregivers (separate from dose logs)."""

    patient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="medication_reports",
    )
    report_date = models.DateField()
    summary = models.TextField(
        help_text="What was administered, changes, side effects, etc.",
    )
    recorded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medication_reports_authored",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-report_date", "-id"]
        indexes = [
            models.Index(fields=["patient", "-report_date"]),
        ]

    def __str__(self):
        return f"Med report {self.patient_id} {self.report_date}"
