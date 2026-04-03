from django.db import models

from apps.accounts.models import CustomUser


class PatientVitalReading(models.Model):
    """Point-in-time vital signs (multiple readings per day allowed)."""

    patient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="vital_readings",
    )
    recorded_at = models.DateTimeField(
        help_text="When the measurement was taken (wall clock).",
    )
    recorded_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vital_readings_recorded",
    )
    systolic_mmhg = models.PositiveSmallIntegerField(null=True, blank=True)
    diastolic_mmhg = models.PositiveSmallIntegerField(null=True, blank=True)
    heart_rate_bpm = models.PositiveSmallIntegerField(null=True, blank=True)
    temperature_celsius = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
    )
    spo2_percent = models.PositiveSmallIntegerField(null=True, blank=True)
    respiratory_rate = models.PositiveSmallIntegerField(null=True, blank=True)
    blood_glucose_mg_dl = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at", "-id"]
        indexes = [
            models.Index(fields=["patient", "-recorded_at"]),
        ]

    def __str__(self):
        return f"Vitals {self.patient_id} @ {self.recorded_at}"
