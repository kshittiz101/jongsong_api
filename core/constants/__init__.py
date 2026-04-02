"""
Core constants package.

This package supersedes the historical `core/constants.py` module.
"""

# Max size for profile / citizenship / medicine image uploads (matches validators + upload caps).
IMAGE_UPLOAD_MAX_BYTES = 500 * 1024  # 500 KiB

# Hero banner images: larger than general uploads; tune max as needed.
HERO_IMAGE_MIN_BYTES = 1024 * 1024  # 1 MiB
HERO_IMAGE_MAX_BYTES = 10 * 1024 * 1024  # 10 MiB
