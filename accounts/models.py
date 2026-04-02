from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from core.image_validators import validate_image_file_integrity, validate_image_file_size
from core.constants.roles import Role


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:  # pragma: no cover
            raise ValueError("An email address is required.")

        email = self.normalize_email(email)
        extra_fields.setdefault("username", email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email=email, password=password, **extra_fields)


class CustomUser(AbstractUser):
    """Custom user that uses email as the login identifier."""
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number"]

    objects = CustomUserManager()
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email)
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username



class Designation(models.Model):
    """
    This model is used to store the designation information.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


def default_other_designation_pk():
    """DB default for profiles; matches the seeded \"Other\" designation (see migration 0004)."""
    return Designation.objects.filter(name="Other").values_list("pk", flat=True).first()


class AdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="admin_profile")
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