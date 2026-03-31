from django.core.exceptions import ValidationError
from django.db import models
from pharmacy.models import Category


def _validate_image_size_2mb(file_obj):
    size = getattr(file_obj, "size", None)
    if size is None:
        return
    if size > 2 * 1024 * 1024:
        raise ValidationError("Image file too large (max 2 MB).")


def _validate_image_size_3mb(file_obj):
    size = getattr(file_obj, "size", None)
    if size is None:
        return
    if size > 3 * 1024 * 1024:
        raise ValidationError("Image file too large (max 3 MB).")


class HeroImage(models.Model):
    '''
    HeroImage model stores all hero image details including image, title, description, and timestamps.
    '''
    image = models.ImageField(upload_to='hero_images/', validators=[_validate_image_size_3mb])
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='hero_images')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title




class Feature(models.Model):
    '''
    Feature model stores all feature details including title, description, icon name, and timestamps.
    '''
    title = models.CharField(max_length=255)
    description = models.TextField()
    icon_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Services(models.Model):
    '''
    Services model stores all services details including title, description, icon name, and timestamps.
    '''
    COLOR_CHOICES = [
        ("primary", "Primary"),
        ("secondary", "Secondary"),
        ("success", "Success"),
        ("danger", "Danger"),
        ("warning", "Warning"),
        ("info", "Info"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    icon_name = models.CharField(max_length=255)
    rank = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default="primary")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["rank", "id"]

    def __str__(self):
        return self.title