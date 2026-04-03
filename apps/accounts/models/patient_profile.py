import secrets

from django.core.exceptions import ValidationError
from django.db import models

from common.constants.blood_groups import BloodGroup
from common.constants.genders import Gender
from common.constants.patient_types import PatientType
from common.constants.roles import Role

from .public_user_profile import PublicUserProfile
from .user import CustomUser


class PatientProfile(models.Model):
    """
    Patient profile linked one-to-one to CustomUser.
    When unique_health_id is blank, save() assigns an internal JSC-PAT-* id.
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="patient_profile",
    )

    unique_health_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
    )

    patient_type = models.CharField(
        max_length=100,
        choices=PatientType.choices,
        default=PatientType.OTHER,
        null=True,
        blank=True,
    )
    role = models.CharField(
        max_length=100,
        choices=Role.choices,
        default=Role.PATIENT,
        null=True,
        blank=True,
    )

    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(
        max_length=5,
        choices=BloodGroup.choices,
        null=True,
        blank=True,
    )
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        null=True,
        blank=True,
    )

    emergency_contact_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    emergency_contact_phone = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    emergency_contact_relation = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    chronic_conditions = models.TextField(
        blank=True,
        null=True,
        help_text="List of chronic diseases",
    )
    allergies = models.TextField(
        blank=True,
        null=True,
        help_text="Known allergies",
    )
    previous_surgeries = models.TextField(blank=True, null=True)
    family_history = models.TextField(blank=True, null=True)

    home_address = models.TextField(null=True, blank=True)
    preferred_care_time = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    special_instructions = models.TextField(blank=True, null=True)
    requires_24h_care = models.BooleanField(null=True, blank=True)
    is_active_patient = models.BooleanField(null=True, blank=True)

    admission_date = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
    )
    discharge_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-admission_date"]
        verbose_name = "patient profile"
        verbose_name_plural = "patient profiles"

    def __str__(self):
        if self.user_id:
            return f"Patient Profile of {self.user.username}"
        return f"Patient Profile (pk={self.pk!r})"

    def clean(self):
        if self.discharge_date and self.admission_date:
            if self.discharge_date.date() < self.admission_date.date():
                raise ValidationError(
                    {
                        "discharge_date": (
                            "Discharge date cannot be before admission date."
                        )
                    }
                )

    def save(self, *args, **kwargs):
        uid = self.unique_health_id
        if uid is None or (isinstance(uid, str) and not uid.strip()):
            self.unique_health_id = f"JSC-PAT-{secrets.token_hex(4).upper()}"
        super().save(*args, **kwargs)
        if self.user_id is None or self.role is None:
            return
        pub = getattr(self.user, "publicuserprofile", None)
        if pub is not None and pub.role != self.role:
            PublicUserProfile.objects.filter(pk=pub.pk).update(role=self.role)
