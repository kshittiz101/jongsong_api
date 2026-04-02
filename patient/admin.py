from django.contrib import admin

from .models import PatientProfile


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "unique_health_id",
        "user",
        "role",
        "patient_type",
        "is_active_patient",
        "admission_date",
    )
    list_filter = ("patient_type", "role", "is_active_patient", "gender")
    search_fields = ("unique_health_id", "user__email", "user__phone_number")
    raw_id_fields = ("user",)
    readonly_fields = (
        "unique_health_id",
        "admission_date",
        "created_at",
        "updated_at",
    )
