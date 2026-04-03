from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import AdminProfile, Designation, PatientProfile, PublicUserProfile
from common.constants.blood_groups import BloodGroup
from common.constants.genders import Gender
from common.constants.patient_types import PatientType
from common.constants.roles import Role

User = get_user_model()

_MINIMAL_ONBOARDING = {
    "email": "patient1@example.com",
    "phone_number": "9801111111",
    "password": "PatientPass123!@#",
    "password2": "PatientPass123!@#",
    "patient_type": PatientType.HOME_CARE,
    "date_of_birth": "1990-05-01",
    "blood_group": BloodGroup.O_POSITIVE,
    "gender": Gender.MALE,
    "emergency_contact_name": "EC Name",
    "emergency_contact_phone": "9802222222",
    "emergency_contact_relation": "Sibling",
    "home_address": "Kathmandu",
    "role": Role.PATIENT,
}


class PatientProfileModelTests(APITestCase):
    def setUp(self):
        Designation.objects.get_or_create(
            name="Other",
            defaults={"description": ""},
        )
        self.user = User.objects.create_user(
            email="pu@example.com",
            phone_number="9803333333",
            password="x",
        )
        PublicUserProfile.objects.create(user=self.user, role=Role.PATIENT)

    def test_full_clean_rejects_discharge_before_admission(self):
        profile = PatientProfile(
            user=self.user,
            role=Role.PATIENT,
            patient_type=PatientType.HOME_CARE,
            date_of_birth="1980-01-01",
            blood_group=BloodGroup.A_POSITIVE,
            gender=Gender.FEMALE,
            emergency_contact_name="n",
            emergency_contact_phone="9804444444",
            emergency_contact_relation="r",
            home_address="addr",
        )
        admit = timezone.now()
        profile.admission_date = admit
        profile.discharge_date = admit - timedelta(days=1)
        with self.assertRaises(ValidationError):
            profile.full_clean()


class PatientProfileApiTests(APITestCase):
    def setUp(self):
        Designation.objects.get_or_create(
            name="Other",
            defaults={"description": ""},
        )
        self.superuser = User.objects.create_superuser(
            email="root@example.com",
            phone_number="9800000000",
            password="RootPass123!@#",
        )
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            phone_number="9800000001",
            password="AdminPass123!@#",
            is_staff=True,
            is_superuser=False,
        )
        AdminProfile.objects.create(
            user=self.admin_user,
            role=Role.ADMIN,
        )
        self.patient_user = User.objects.create_user(
            email="pat@example.com",
            phone_number="9800000002",
            password="PatPass123!@#",
        )
        PublicUserProfile.objects.create(
            user=self.patient_user,
            role=Role.PATIENT,
        )
        self.profile = PatientProfile.objects.create(
            user=self.patient_user,
            role=Role.PATIENT,
            patient_type=PatientType.HOME_CARE,
            date_of_birth="1991-01-01",
            blood_group=BloodGroup.B_POSITIVE,
            gender=Gender.MALE,
            emergency_contact_name="e",
            emergency_contact_phone="9800000003",
            emergency_contact_relation="brother",
            home_address="Lalitpur",
        )

        self.customer_user = User.objects.create_user(
            email="cust@example.com",
            phone_number="9800000004",
            password="CustPass123!@#",
        )
        PublicUserProfile.objects.create(
            user=self.customer_user,
            role=Role.CUSTOMER,
        )

    def _jwt(self, user):
        res = self.client.post(
            "/api/v1/auth/token/",
            {"email": user.email, "password": self._password_for(user)},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def _password_for(self, user):
        if user == self.superuser:
            return "RootPass123!@#"
        if user == self.admin_user:
            return "AdminPass123!@#"
        if user == self.patient_user:
            return "PatPass123!@#"
        if user == self.customer_user:
            return "CustPass123!@#"
        return "x"

    def test_superuser_can_onboard_patient_user(self):
        self._jwt(self.superuser)
        payload = {
            **_MINIMAL_ONBOARDING,
            "email": "newpat@example.com",
            "phone_number": "9811111111",
        }
        res = self.client.post(
            "/api/v1/admin/patient-users/",
            payload,
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        u = User.objects.get(email="newpat@example.com")
        self.assertEqual(u.publicuserprofile.role, Role.PATIENT)
        self.assertTrue(hasattr(u, "patient_profile"))
        self.assertEqual(u.patient_profile.role, Role.PATIENT)

    def test_onboarding_rejects_non_patient_role(self):
        self._jwt(self.superuser)
        payload = {
            **_MINIMAL_ONBOARDING,
            "email": "badrole@example.com",
            "phone_number": "9812222222",
            "role": Role.CUSTOMER,
        }
        res = self.client.post(
            "/api/v1/admin/patient-users/",
            payload,
            format="json",
        )
        self.assertEqual(res.status_code, 400, res.data)

    def test_admin_can_list_patient_profiles(self):
        self._jwt(self.admin_user)
        res = self.client.get("/api/v1/admin/patient-profiles/", format="json")
        self.assertEqual(res.status_code, 200, res.data)
        results = res.data.get("results", res.data)
        self.assertGreaterEqual(len(results), 1)

    def test_patient_can_get_me(self):
        self._jwt(self.patient_user)
        res = self.client.get("/api/v1/admin/patient-profiles/me/", format="json")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data["id"], self.profile.id)

    def test_patient_gets_404_for_other_profile_pk(self):
        other = User.objects.create_user(
            email="pat2@example.com",
            phone_number="9800000005",
            password="PatPass123!@#",
        )
        PublicUserProfile.objects.create(user=other, role=Role.PATIENT)
        other_profile = PatientProfile.objects.create(
            user=other,
            role=Role.PATIENT,
            patient_type=PatientType.HOME_CARE,
            date_of_birth="1992-01-01",
            blood_group=BloodGroup.O_POSITIVE,
            gender=Gender.FEMALE,
            emergency_contact_name="e2",
            emergency_contact_phone="9800000006",
            emergency_contact_relation="sister",
            home_address="Pokhara",
        )
        self._jwt(self.patient_user)
        res = self.client.get(
            f"/api/v1/admin/patient-profiles/{other_profile.pk}/", format="json"
        )
        self.assertEqual(res.status_code, 404, res.data)

    def test_create_profile_rejects_non_patient_public_role(self):
        self._jwt(self.superuser)
        res = self.client.post(
            "/api/v1/admin/patient-profiles/",
            {
                "user": self.customer_user.pk,
                "patient_type": PatientType.HOME_CARE,
                "date_of_birth": "1993-01-01",
                "blood_group": BloodGroup.A_POSITIVE,
                "gender": Gender.MALE,
                "emergency_contact_name": "e",
                "emergency_contact_phone": "9800000007",
                "emergency_contact_relation": "x",
                "home_address": "addr",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 400, res.data)

    def test_create_profile_rejects_duplicate_for_same_user(self):
        self._jwt(self.superuser)
        lone = User.objects.create_user(
            email="lone@example.com",
            phone_number="9800000008",
            password="LonePass123!@#",
        )
        PublicUserProfile.objects.create(user=lone, role=Role.PATIENT)
        PatientProfile.objects.create(
            user=lone,
            role=Role.PATIENT,
            patient_type=PatientType.HOME_CARE,
            date_of_birth="1994-01-01",
            blood_group=BloodGroup.AB_POSITIVE,
            gender=Gender.OTHER,
            emergency_contact_name="e",
            emergency_contact_phone="9800000009",
            emergency_contact_relation="x",
            home_address="addr",
        )
        res = self.client.post(
            "/api/v1/admin/patient-profiles/",
            {
                "user": lone.pk,
                "patient_type": PatientType.HOME_CARE,
                "date_of_birth": "1994-02-01",
                "blood_group": BloodGroup.AB_POSITIVE,
                "gender": Gender.OTHER,
                "emergency_contact_name": "e",
                "emergency_contact_phone": "9800000010",
                "emergency_contact_relation": "x",
                "home_address": "addr2",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 400, res.data)
