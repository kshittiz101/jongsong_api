from django.db import models

from common.constants.roles import Role
from common.image_validators import validate_image_file_integrity, validate_image_file_size

from .designation import Designation, default_other_designation_pk
from .user import CustomUser


class StaffProfile(models.Model):
    """
    This model is used to store the staff profile information.
    """

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="staff_profile"
    )
    role = models.CharField(
        max_length=100, choices=Role.choices, default=Role.STAFF
    )
    designation = models.ForeignKey(
        Designation,
        on_delete=models.PROTECT,
        related_name="staff_profiles",
        default=default_other_designation_pk,
    )

    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        null=True,
        blank=True,
        validators=[validate_image_file_integrity, validate_image_file_size],
    )
    highest_degree = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, default="")
    citizenship_image = models.ImageField(
        upload_to="citizenship_images/",
        null=True,
        blank=True,
        validators=[validate_image_file_integrity, validate_image_file_size],
    )
    field_of_study = models.CharField(max_length=100, blank=True, null=True)
    university = models.CharField(max_length=200, blank=True, null=True)
    graduation_year = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of : {self.user.username}"
