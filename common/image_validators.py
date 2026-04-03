"""
Validators for user-uploaded images (used with Pillow-backed ImageField).
"""

from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

from .constants import (
    HERO_IMAGE_MAX_BYTES,
    HERO_IMAGE_MIN_BYTES,
    IMAGE_UPLOAD_MAX_BYTES,
)


def validate_image_file_size(file):
    """Reject files larger than IMAGE_UPLOAD_MAX_BYTES."""
    size = getattr(file, "size", None)
    if size is None:
        return
    if size > IMAGE_UPLOAD_MAX_BYTES:
        if IMAGE_UPLOAD_MAX_BYTES >= 1024 * 1024:
            max_label = f"{IMAGE_UPLOAD_MAX_BYTES / (1024 * 1024):.0f} MB"
        else:
            max_label = f"{IMAGE_UPLOAD_MAX_BYTES // 1024} KB"
        raise ValidationError(f"Image file must be at most {max_label}.")


def validate_hero_image_file_size(file):
    """Hero images must be within HERO_IMAGE_MIN_BYTES..HERO_IMAGE_MAX_BYTES."""
    size = getattr(file, "size", None)
    if size is None:
        return
    if size < HERO_IMAGE_MIN_BYTES:
        raise ValidationError(
            f"Hero image must be at least {HERO_IMAGE_MIN_BYTES // (1024 * 1024)} MB."
        )
    if size > HERO_IMAGE_MAX_BYTES:
        raise ValidationError(
            f"Hero image must be at most {HERO_IMAGE_MAX_BYTES // (1024 * 1024)} MB."
        )


def validate_image_file_integrity(file):
    """
    Ensure the uploaded file is a readable image (catches truncated/corrupt files).
    """
    file.seek(0)
    try:
        with Image.open(file) as img:
            img.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValidationError('Invalid or corrupted image file.') from exc
    finally:
        file.seek(0)

    try:
        with Image.open(file) as img:
            img.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValidationError('Invalid or corrupted image file.') from exc
    finally:
        file.seek(0)
