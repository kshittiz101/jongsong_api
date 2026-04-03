from django.db import models

from common.constants.roles import Role
from common.image_validators import validate_image_file_integrity, validate_image_file_size

from .designation import Designation, default_other_designation_pk
from .user import CustomUser


class AdminProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="admin_profile"
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        null=True,
        blank=True,
        validators=[validate_image_file_integrity, validate_image_file_size],
    )
    role = models.CharField(
        max_length=100,
        choices=Role.choices,
        default=Role.ADMIN,
    )
    designation = models.ForeignKey(
        Designation,
        on_delete=models.PROTECT,
        related_name="admin_profiles",
        default=default_other_designation_pk,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Admin Profile of {self.user.username}"
