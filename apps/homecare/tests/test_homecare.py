from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import (
    AdminProfile,
    Designation,
    PatientProfile,
    PublicUserProfile,
    StaffProfile,
)
from common.constants.blood_groups import BloodGroup
from common.constants.genders import Gender
from common.constants.patient_types import PatientType
from common.constants.roles import Role

from apps.homecare.models import PatientCareAssignment, PatientVitalReading

User = get_user_model()


class HomeCareApiTests(APITestCase):
    def setUp(self):
        Designation.objects.get_or_create(
            name="Other",
            defaults={"description": ""},
        )
        self.admin_user = User.objects.create_user(
            email="hcadmin@example.com",
            phone_number="9801000001",
            password="AdminPass123!@#",
            is_staff=True,
            is_superuser=False,
        )
        AdminProfile.objects.create(
            user=self.admin_user,
            role=Role.ADMIN,
        )
        self.patient_user = User.objects.create_user(
            email="hcpat@example.com",
            phone_number="9801000002",
            password="PatPass123!@#",
        )
        PublicUserProfile.objects.create(
            user=self.patient_user,
            role=Role.PATIENT,
        )
        PatientProfile.objects.create(
            user=self.patient_user,
            role=Role.PATIENT,
            patient_type=PatientType.HOME_CARE,
            date_of_birth="1991-01-01",
            blood_group=BloodGroup.B_POSITIVE,
            gender=Gender.MALE,
            emergency_contact_name="e",
            emergency_contact_phone="9801000003",
            emergency_contact_relation="brother",
            home_address="Lalitpur",
        )
        self.nurse_user = User.objects.create_user(
            email="nurse@example.com",
            phone_number="9801000004",
            password="NursePass123!@#",
        )
        PublicUserProfile.objects.create(
            user=self.nurse_user,
            role=Role.STAFF,
        )
        StaffProfile.objects.create(user=self.nurse_user, role=Role.STAFF)
        self.doctor_user = User.objects.create_user(
            email="doctor@example.com",
            phone_number="9801000005",
            password="DocPass123!@#",
        )
        PublicUserProfile.objects.create(
            user=self.doctor_user,
            role=Role.STAFF,
        )
        StaffProfile.objects.create(user=self.doctor_user, role=Role.STAFF)

    def _jwt(self, user):
        passwords = {
            self.admin_user: "AdminPass123!@#",
            self.patient_user: "PatPass123!@#",
            self.nurse_user: "NursePass123!@#",
            self.doctor_user: "DocPass123!@#",
        }
        res = self.client.post(
            "/api/v1/auth/token/",
            {"email": user.email, "password": passwords[user]},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_admin_can_create_care_assignment(self):
        self._jwt(self.admin_user)
        res = self.client.post(
            "/api/v1/admin/home-care/care-assignments/",
            {
                "patient": self.patient_user.pk,
                "doctor": self.doctor_user.pk,
                "nurse": self.nurse_user.pk,
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        self.assertTrue(
            PatientCareAssignment.objects.filter(
                patient_id=self.patient_user.pk,
                is_active=True,
            ).exists()
        )

    def test_patient_can_record_own_vitals(self):
        self._jwt(self.patient_user)
        ts = timezone.now()
        res = self.client.post(
            "/api/v1/admin/home-care/vitals/",
            {
                "patient": self.patient_user.pk,
                "recorded_at": ts.isoformat(),
                "systolic_mmhg": 118,
                "diastolic_mmhg": 76,
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(PatientVitalReading.objects.count(), 1)

    def test_assigned_nurse_can_record_patient_vitals(self):
        PatientCareAssignment.objects.create(
            patient=self.patient_user,
            doctor=self.doctor_user,
            nurse=self.nurse_user,
            is_active=True,
        )
        self._jwt(self.nurse_user)
        ts = timezone.now()
        res = self.client.post(
            "/api/v1/admin/home-care/vitals/",
            {
                "patient": self.patient_user.pk,
                "recorded_at": ts.isoformat(),
                "heart_rate_bpm": 72,
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
