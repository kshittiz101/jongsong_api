from django.contrib import admin

from home.models import Feature, Services, HeroImage


@admin.register(HeroImage)
class HeroImageAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "category", "created_at", "updated_at")
    search_fields = ("title", "description", "category")
    ordering = ("-id",)

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "icon_name", "created_at", "updated_at")
    search_fields = ("title", "description", "icon_name")
    ordering = ("-id",)


@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ("rank", "title", "color", "icon_name", "created_at", "updated_at")
    list_filter = ("color",)
    search_fields = ("title", "description", "icon_name")
    ordering = ("rank", "id")
