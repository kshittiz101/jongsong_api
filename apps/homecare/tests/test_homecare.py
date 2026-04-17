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

from apps.homecare.models import PatientVitalReading

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

    def test_nurse_cannot_record_other_patient_vitals(self):
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
        self.assertEqual(res.status_code, 403, res.data)


_HC_PORTAL_CREATE_PAYLOAD = {
    "email": "hcportalnew@example.com",
    "phone_number": "9813888888",
    "password": "PatientPass123!@#",
    "password2": "PatientPass123!@#",
    "date_of_birth": "1990-05-01",
    "blood_group": BloodGroup.O_POSITIVE,
    "gender": Gender.MALE,
    "emergency_contact_name": "EC",
    "emergency_contact_phone": "9813888889",
    "emergency_contact_relation": "Parent",
    "home_address": "Kathmandu",
    "role": Role.PATIENT,
}


class HomeCarePatientPortalApiTests(APITestCase):
    """Admin portal: `/api/v1/admin/home-care/patients/`."""

    def setUp(self):
        Designation.objects.get_or_create(
            name="Other",
            defaults={"description": ""},
        )
        self.admin_user = User.objects.create_user(
            email="hcpadmin@example.com",
            phone_number="9802000001",
            password="AdminPass123!@#",
            is_staff=True,
            is_superuser=False,
        )
        AdminProfile.objects.create(user=self.admin_user, role=Role.ADMIN)

        self.hc_patient = User.objects.create_user(
            email="hcpuser@example.com",
            phone_number="9802000002",
            password="PatPass123!@#",
        )
        PublicUserProfile.objects.create(user=self.hc_patient, role=Role.PATIENT)
        PatientProfile.objects.create(
            user=self.hc_patient,
            role=Role.PATIENT,
            patient_type=PatientType.HOME_CARE,
            date_of_birth="1991-01-01",
            blood_group=BloodGroup.B_POSITIVE,
            gender=Gender.MALE,
            emergency_contact_name="e",
            emergency_contact_phone="9802000003",
            emergency_contact_relation="brother",
            home_address="Lalitpur",
        )

        self.pharmacy_patient = User.objects.create_user(
            email="pharmpat@example.com",
            phone_number="9802000004",
            password="PatPass123!@#",
        )
        PublicUserProfile.objects.create(user=self.pharmacy_patient, role=Role.PATIENT)
        PatientProfile.objects.create(
            user=self.pharmacy_patient,
            role=Role.PATIENT,
            patient_type=PatientType.PHARMACY,
            date_of_birth="1992-01-01",
            blood_group=BloodGroup.A_POSITIVE,
            gender=Gender.FEMALE,
            emergency_contact_name="e2",
            emergency_contact_phone="9802000005",
            emergency_contact_relation="sister",
            home_address="Patan",
        )

        self.nurse_user = User.objects.create_user(
            email="hcpnurse@example.com",
            phone_number="9802000006",
            password="NursePass123!@#",
        )
        PublicUserProfile.objects.create(user=self.nurse_user, role=Role.STAFF)
        StaffProfile.objects.create(user=self.nurse_user, role=Role.STAFF)

    def _jwt(self, user):
        passwords = {
            self.admin_user: "AdminPass123!@#",
            self.hc_patient: "PatPass123!@#",
            self.pharmacy_patient: "PatPass123!@#",
            self.nurse_user: "NursePass123!@#",
        }
        res = self.client.post(
            "/api/v1/auth/token/",
            {"email": user.email, "password": passwords[user]},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_admin_list_returns_only_home_care(self):
        self._jwt(self.admin_user)
        res = self.client.get("/api/v1/admin/home-care/patients/", format="json")
        self.assertEqual(res.status_code, 200, res.data)
        results = res.data.get("results", res.data)
        self.assertIsInstance(results, list)
        for row in results:
            self.assertEqual(row["patient_type"], PatientType.HOME_CARE)
        user_ids = {r["user"]["id"] for r in results}
        self.assertIn(self.hc_patient.pk, user_ids)
        self.assertNotIn(self.pharmacy_patient.pk, user_ids)

    def test_admin_list_phone_number_filter(self):
        self._jwt(self.admin_user)
        res = self.client.get(
            "/api/v1/admin/home-care/patients/",
            {"phone_number": "9802000002"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        results = res.data.get("results", res.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["user"]["id"], self.hc_patient.pk)

    def test_nurse_forbidden_list_and_create(self):
        self._jwt(self.nurse_user)
        res = self.client.get("/api/v1/admin/home-care/patients/", format="json")
        self.assertEqual(res.status_code, 403, res.data)
        res2 = self.client.post(
            "/api/v1/admin/home-care/patients/",
            _HC_PORTAL_CREATE_PAYLOAD,
            format="json",
        )
        self.assertEqual(res2.status_code, 403, res2.data)

    def test_patient_forbidden_list(self):
        self._jwt(self.hc_patient)
        res = self.client.get("/api/v1/admin/home-care/patients/", format="json")
        self.assertEqual(res.status_code, 403, res.data)

    def test_admin_create_forces_home_care_without_patient_type_in_body(self):
        self._jwt(self.admin_user)
        res = self.client.post(
            "/api/v1/admin/home-care/patients/",
            _HC_PORTAL_CREATE_PAYLOAD,
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data["patient_type"], PatientType.HOME_CARE)
        u = User.objects.get(email="hcportalnew@example.com")
        self.assertEqual(u.patient_profile.patient_type, PatientType.HOME_CARE)

    def test_admin_retrieve_and_patch(self):
        self._jwt(self.admin_user)
        url = f"/api/v1/admin/home-care/patients/{self.hc_patient.pk}/"
        res = self.client.get(url, format="json")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data["user"]["id"], self.hc_patient.pk)

        res2 = self.client.patch(
            url,
            {"first_name": "Updated", "home_address": "Bhaktapur"},
            format="json",
        )
        self.assertEqual(res2.status_code, 200, res2.data)
        self.hc_patient.refresh_from_db()
        self.assertEqual(self.hc_patient.first_name, "Updated")
        self.assertEqual(
            PatientProfile.objects.get(user=self.hc_patient).home_address,
            "Bhaktapur",
        )
