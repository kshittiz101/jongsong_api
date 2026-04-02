from django.contrib import admin
from .models import CustomUser, Designation


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "description"]
    search_fields = ["name"]


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "phone_number", "is_staff", "is_active"]

