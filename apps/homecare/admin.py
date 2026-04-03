from django.contrib import admin

from .models import (
    Medication,
    MedicationLog,
    MedicationReport,
    PatientCareAssignment,
    PatientVitalReading,
)


class MedicationLogInline(admin.TabularInline):
    model = MedicationLog
    extra = 0
    raw_id_fields = ("marked_by",)


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "medication_name",
        "patient",
        "form",
        "frequency",
        "is_active",
        "start_date",
        "created_at",
    )
    list_filter = ("form", "frequency", "is_active", "refill_reminder")
    search_fields = (
        "medication_name",
        "dosage",
        "patient__email",
        "patient__phone_number",
    )
    raw_id_fields = ("patient",)
    readonly_fields = ("created_at", "updated_at")
    inlines = (MedicationLogInline,)


@admin.register(MedicationLog)
class MedicationLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "medication",
        "scheduled_time",
        "status",
        "actual_taken_time",
        "marked_by",
    )
    list_filter = ("status",)
    search_fields = ("medication__medication_name", "notes")
    raw_id_fields = ("medication", "marked_by")


@admin.register(PatientVitalReading)
class PatientVitalReadingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "recorded_at",
        "systolic_mmhg",
        "diastolic_mmhg",
        "heart_rate_bpm",
        "temperature_celsius",
        "spo2_percent",
    )
    list_filter = ("recorded_at",)
    search_fields = ("patient__email", "notes")
    raw_id_fields = ("patient", "recorded_by")
    date_hierarchy = "recorded_at"


@admin.register(MedicationReport)
class MedicationReportAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "report_date", "recorded_by", "created_at")
    list_filter = ("report_date",)
    search_fields = ("summary", "patient__email")
    raw_id_fields = ("patient", "recorded_by")
    date_hierarchy = "report_date"


@admin.register(PatientCareAssignment)
class PatientCareAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "doctor",
        "nurse",
        "is_active",
        "assigned_at",
        "ended_at",
    )
    list_filter = ("is_active",)
    search_fields = ("patient__email", "notes")
    raw_id_fields = ("patient", "doctor", "nurse")
