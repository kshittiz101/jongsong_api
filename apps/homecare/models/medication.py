from django.db import models

from apps.accounts.models import CustomUser

FORM_CHOICES = (
    ("tablet", "Tablet"),
    ("capsule", "Capsule"),
    ("syrup", "Syrup"),
    ("injection", "Injection"),
)

FREQUENCY_CHOICES = (
    ("daily", "Daily"),
    ("twice_daily", "Twice Daily"),
    ("weekly", "Weekly"),
    ("as_needed", "As needed"),
)


class Medication(models.Model):
    """Medication schedule and details for a patient user."""

    patient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="medications",
    )
    medication_name = models.CharField(max_length=200, null=True, blank=True)
    dosage = models.CharField(
        max_length=100,
        help_text="e.g., 500mg",
        null=True,
        blank=True,
    )
    form = models.CharField(
        max_length=50,
        choices=FORM_CHOICES,
        null=True,
        blank=True,
    )
    quantity = models.PositiveIntegerField(default=0, null=True, blank=True)
    refill_reminder = models.BooleanField(default=False, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    frequency = models.CharField(
        max_length=50,
        choices=FREQUENCY_CHOICES,
        null=True,
        blank=True,
    )
    times = models.JSONField(
        default=None,
        null=True,
        blank=True,
        help_text="List of times for medication intake",
    )
    instructions = models.TextField(
        blank=True,
        null=True,
        help_text="Special instructions for intake",
    )
    is_active = models.BooleanField(default=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        name = self.medication_name or "Medication"
        if self.patient_id:
            return f"{name} — {self.patient.get_full_name() or self.patient.email}"
        return name


class MedicationLog(models.Model):
    """Per-dose medication adherence (scheduled vs actual time, status)."""

    medication = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name="logs",
        null=True,
        blank=True,
    )
    scheduled_time = models.DateTimeField(null=True, blank=True)
    actual_taken_time = models.DateTimeField(null=True, blank=True)

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("taken", "Taken"),
        ("missed", "Missed"),
        ("delayed", "Delayed"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True, null=True)
    marked_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medication_logs_marked",
    )

    class Meta:
        ordering = ["-scheduled_time", "-id"]

    def __str__(self):
        med = self.medication
        label = med.medication_name if med else "—"
        return f"{label} @ {self.scheduled_time} ({self.status})"
