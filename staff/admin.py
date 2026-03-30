from django.contrib import admin
from staff.models import StaffProfile
# Register your models here.
@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_picture', 'highest_degree', 'field_of_study', 'university', 'graduation_year']
