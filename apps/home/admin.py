from django.contrib import admin
from .models import Feature, Services, HeroImage, Location


@admin.register(HeroImage)
class HeroImageAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description",
                    "category", "created_at", "updated_at")
    search_fields = ("title", "description", "category")
    ordering = ("-id",)


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "icon_name", "created_at", "updated_at")
    search_fields = ("title", "description", "icon_name")
    ordering = ("-id",)


@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ("rank", "title", "color", "icon_name",
                    "created_at", "updated_at")
    list_filter = ("color",)
    search_fields = ("title", "description", "icon_name")
    ordering = ("rank", "id")


class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'postal_code', 'created_at']
    list_filter = ['city', 'created_at']
    search_fields = ['name', 'street', 'city']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'street', 'city', 'postal_code')
        }),
        ('Google Maps', {
            'fields': ('google_location_links', 'google_maps_embed'),
            'description': 'Paste the iframe embed code from Google Maps'
        }),
    )

    readonly_fields = ['created_at']


admin.site.register(Location, LocationAdmin)
