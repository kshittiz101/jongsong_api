from django.core.validators import FileExtensionValidator
from django.db import models

from apps.pharmacy.models import Category
from common.image_validators import validate_hero_image_file_size

_HERO_IMAGE_VALIDATORS = [
    FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
    validate_hero_image_file_size,
]


class HeroImage(models.Model):
    """
    HeroImage model stores all hero image details including image, title, description, and timestamps.
    """

    image = models.ImageField(upload_to="hero_images/", validators=_HERO_IMAGE_VALIDATORS)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="hero_images",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
