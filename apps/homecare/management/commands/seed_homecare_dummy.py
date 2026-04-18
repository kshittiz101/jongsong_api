"""
Create dummy home-care demo users: one patient and two home-care staff (nurse + staff).

Idempotent: safe to run multiple times (skips or links existing rows by email).

Usage:
  pipenv run python manage.py seed_homecare_dummy
  pipenv run python manage.py seed_homecare_dummy --password 'YourPass123!'
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.accounts.models import Designation, PatientProfile, PublicUserProfile, StaffProfile
from common.constants.blood_groups import BloodGroup
from common.constants.genders import Gender
from common.constants.patient_types import PatientType
from common.constants.roles import Role

User = get_user_model()

DEFAULT_PASSWORD = "DemoPass123!@#"

PATIENT_EMAIL = "dummy.hcpatient@jongsong.demo"
NURSE_EMAIL = "dummy.nurse@jongsong.demo"
HC_STAFF_EMAIL = "dummy.hcstaff@jongsong.demo"

PATIENT_PHONE = "977981111001"
NURSE_PHONE = "977981111002"
HC_STAFF_PHONE = "977981111003"


class Command(BaseCommand):
    help = "Seed dummy home-care patient + home-care staff (nurse + second staff) for local/demo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default=DEFAULT_PASSWORD,
            help=f"Password for newly created users only (default: {DEFAULT_PASSWORD}).",
        )

    def handle(self, *args, **options):
        password = options["password"]
        designation, _ = Designation.objects.get_or_create(
            name="Other",
            defaults={"description": "Default designation"},
        )

        self._ensure_patient(password)
        self._ensure_staff(NURSE_EMAIL, NURSE_PHONE, password, designation, "Jane", "Nurse")
        self._ensure_staff(HC_STAFF_EMAIL, HC_STAFF_PHONE, password, designation, "Alex", "HomeCare")

        self.stdout.write(self.style.SUCCESS("Done. Logins (if users were just created, use your password):"))
        self.stdout.write(f"  Patient:        {PATIENT_EMAIL}")
        self.stdout.write(f"  Nurse (staff):  {NURSE_EMAIL}")
        self.stdout.write(f"  HC staff:       {HC_STAFF_EMAIL}")

    def _ensure_patient(self, password: str) -> None:
        user, created = User.objects.get_or_create(
            email=PATIENT_EMAIL,
            defaults={
                "phone_number": PATIENT_PHONE,
                "first_name": "Dummy",
                "last_name": "Patient",
                "is_staff": False,
                "is_superuser": False,
            },
        )
        if created:
            user.set_password(password)
            user.save(update_fields=["password"])
            self.stdout.write(self.style.NOTICE(f"Created user {PATIENT_EMAIL}"))
        else:
            self.stdout.write(f"User already exists: {PATIENT_EMAIL}")

        PublicUserProfile.objects.update_or_create(
            user=user,
            defaults={"role": Role.PATIENT},
        )
        PatientProfile.objects.update_or_create(
            user=user,
            defaults={
                "role": Role.PATIENT,
                "patient_type": PatientType.HOME_CARE,
                "date_of_birth": "1965-06-15",
                "blood_group": BloodGroup.O_POSITIVE,
                "gender": Gender.FEMALE,
                "emergency_contact_name": "Demo Contact",
                "emergency_contact_phone": "977980000000",
                "emergency_contact_relation": "Family",
                "home_address": "Demo Street, Kathmandu",
            },
        )
        self.stdout.write(self.style.SUCCESS("Home-care patient profile OK."))

    def _ensure_staff(
        self,
        email: str,
        phone: str,
        password: str,
        designation: Designation,
        first_name: str,
        last_name: str,
    ) -> None:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "phone_number": phone,
                "first_name": first_name,
                "last_name": last_name,
                "is_staff": True,
                "is_superuser": False,
            },
        )
        if created:
            user.set_password(password)
            user.save(update_fields=["password"])
            self.stdout.write(self.style.NOTICE(f"Created user {email}"))
        else:
            self.stdout.write(f"User already exists: {email}")

        PublicUserProfile.objects.update_or_create(
            user=user,
            defaults={"role": Role.CUSTOMER},
        )
        StaffProfile.objects.update_or_create(
            user=user,
            defaults={
                "role": Role.HOME_CARE_STAFF,
                "designation": designation,
            },
        )
        self.stdout.write(self.style.SUCCESS(f"Home-care staff OK: {email}"))
