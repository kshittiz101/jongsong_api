"""
Persisted daily clinical snapshot for home-care patients.

`report_date` is the calendar day in Django's default timezone (`settings.TIME_ZONE`).
Aggregation windows use [start_of_day, end_of_day) in that zone.
"""

from django.conf import settings
from django.db import models

from apps.accounts.models import CustomUser


class PatientDailyClinicalReport(models.Model):
    """Combined medication + vitals snapshot for one patient calendar day."""

    patient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="daily_clinical_reports",
    )
    report_date = models.DateField(
        db_index=True,
        help_text=f"Calendar day in {settings.TIME_ZONE} (see settings.TIME_ZONE).",
    )
    medication_summary = models.JSONField(
        default=dict,
        help_text="Structured medication adherence for the day (logs + optional schedule context).",
    )
    medication_summary_text = models.TextField(blank=True, default="")
    vitals_summary = models.JSONField(
        default=dict,
        help_text="Structured vitals for the day (readings and/or aggregates).",
    )
    vitals_summary_text = models.TextField(blank=True, default="")
    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-report_date", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["patient", "report_date"],
                name="uniq_patient_daily_clinical_report",
            ),
        ]
        indexes = [
            models.Index(fields=["patient", "-report_date"]),
        ]

    def __str__(self):
        return f"Daily clinical {self.patient_id} {self.report_date}"
