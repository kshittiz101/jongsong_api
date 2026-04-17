from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.accounts.models import AdminProfile, PatientProfile, PublicUserProfile, StaffProfile
from common.constants.blood_groups import BloodGroup
from common.constants.genders import Gender
from common.constants.patient_types import PatientType
from common.constants.roles import Role

User = get_user_model()


class UserListApiTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email="uadmin@example.com",
            phone_number="9811000001",
            password="AdminPass123!@#",
            is_staff=True,
            is_superuser=False,
        )
        AdminProfile.objects.create(user=self.admin_user, role=Role.ADMIN)

        self.patient_user = User.objects.create_user(
            email="upat@example.com",
            phone_number="9811000002",
            password="PatPass123!@#",
        )
        PublicUserProfile.objects.create(user=self.patient_user, role=Role.PATIENT)
        PatientProfile.objects.create(
            user=self.patient_user,
            role=Role.PATIENT,
            patient_type=PatientType.HOME_CARE,
            date_of_birth="1990-01-01",
            blood_group=BloodGroup.O_POSITIVE,
            gender=Gender.MALE,
            emergency_contact_name="e",
            emergency_contact_phone="9811000003",
            emergency_contact_relation="x",
            home_address="addr",
        )

        self.customer = User.objects.create_user(
            email="ucust@example.com",
            phone_number="9811000004",
            password="CustPass123!@#",
        )
        PublicUserProfile.objects.create(user=self.customer, role=Role.CUSTOMER)

    def _jwt(self, user):
        passwords = {
            self.admin_user: "AdminPass123!@#",
            self.patient_user: "PatPass123!@#",
            self.customer: "CustPass123!@#",
        }
        res = self.client.post(
            "/api/v1/auth/token/",
            {"email": user.email, "password": passwords[user]},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_admin_get_users_patients_only(self):
        self._jwt(self.admin_user)
        res = self.client.get("/api/v1/users/", {"role": "PATIENT"}, format="json")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertIsInstance(res.data, list)
        ids = {row["id"] for row in res.data}
        self.assertIn(self.patient_user.id, ids)
        self.assertNotIn(self.customer.id, ids)
        for row in res.data:
            if row["id"] == self.patient_user.id:
                self.assertIsNotNone(row.get("patient_profile"))
                self.assertEqual(row["patient_profile"]["patient_type"], PatientType.HOME_CARE)

    def test_patient_cannot_list_users(self):
        self._jwt(self.patient_user)
        res = self.client.get("/api/v1/users/", {"role": "PATIENT"}, format="json")
        self.assertEqual(res.status_code, 403, res.data)
