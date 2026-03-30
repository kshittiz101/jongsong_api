"""
Validators for user-uploaded images (used with Pillow-backed ImageField).
"""

from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

from .constants import IMAGE_UPLOAD_MAX_BYTES


def validate_image_file_size(file):
    """Reject files larger than IMAGE_UPLOAD_MAX_BYTES."""
    if file.size > IMAGE_UPLOAD_MAX_BYTES:
        max_mb = IMAGE_UPLOAD_MAX_BYTES / (1024 * 1024)
        raise ValidationError(f'Image file must be at most {max_mb:.0f} MB.')


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
