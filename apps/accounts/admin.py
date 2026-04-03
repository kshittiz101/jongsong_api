from django.contrib import admin

from .models import (
    CustomUser,
    Designation,
    PatientProfile,
    PublicUserProfile,
    StaffProfile,
)


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "description"]
    search_fields = ["name"]


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "email", "phone_number", "is_staff", "is_active"]
    list_display_links = ["id", "username"]
    search_fields = ["email", "username", "phone_number", "first_name", "last_name"]


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "profile_picture",
        "highest_degree",
        "field_of_study",
        "university",
        "graduation_year",
    ]


@admin.register(PublicUserProfile)
class PublicUserProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "role", "created_at"]
    list_filter = ["role"]
    search_fields = ["user__email", "user__phone_number"]


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "unique_health_id",
        "patient_name",
        "user",
        "role",
        "patient_type",
        "is_active_patient",
        "admission_date",
    )
    list_display_links = ("id", "unique_health_id", "patient_name")
    list_filter = ("patient_type", "role", "is_active_patient", "gender")
    search_fields = ("unique_health_id", "user__email", "user__phone_number")
    autocomplete_fields = ("user",)
    readonly_fields = (
        "unique_health_id",
        "admission_date",
        "created_at",
        "updated_at",
    )

    @admin.display(description="Patient name")
    def patient_name(self, obj):
        user = obj.user
        if user is None:
            return "—"
        full = user.get_full_name().strip()
        if full:
            return full
        return user.email or str(user.pk)
