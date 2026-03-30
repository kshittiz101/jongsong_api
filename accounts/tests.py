from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from accounts.models import AdminProfile
from normal_user.models import PublicUserProfile
from staff.models import StaffProfile


class RegistrationApiTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.superuser = User.objects.create_superuser(
            email="root@example.com",
            phone_number="9800000000",
            password="RootPass123!@#",
        )
        self.normal_user = User.objects.create_user(
            email="user@example.com",
            phone_number="9811111111",
            password="UserPass123!@#",
            is_staff=False,
            is_superuser=False,
        )

    def _auth_as_superuser(self):
        res = self.client.post(
            "/api/token/",
            {"email": self.superuser.email, "password": "RootPass123!@#"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def _auth_as_normal_user(self):
        res = self.client.post(
            "/api/token/",
            {"email": self.normal_user.email, "password": "UserPass123!@#"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_public_registration_requires_auth(self):
        res = self.client.post(
            "/api/register/",
            {
                "email": "newpublic@example.com",
                "phone_number": "9822222222",
                "password": "PublicPass123!@#",
                "password2": "PublicPass123!@#",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 401, res.data)

    def test_superuser_can_create_public_user(self):
        self._auth_as_superuser()
        res = self.client.post(
            "/api/register/",
            {
                "email": "newpublic2@example.com",
                "phone_number": "9822222223",
                "password": "PublicPass123!@#",
                "password2": "PublicPass123!@#",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        User = get_user_model()
        user = User.objects.get(email="newpublic2@example.com")
        self.assertTrue(PublicUserProfile.objects.filter(user=user).exists())

    def test_admin_registration_requires_auth(self):
        res = self.client.post(
            "/api/admin/register/",
            {
                "email": "newadmin@example.com",
                "phone_number": "9833333333",
                "password": "AdminPass123!@#",
                "password2": "AdminPass123!@#",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 401, res.data)

    def test_staff_registration_requires_auth(self):
        res = self.client.post(
            "/api/staff/register/",
            {
                "email": "newstaff@example.com",
                "phone_number": "9844444444",
                "password": "StaffPass123!@#",
                "password2": "StaffPass123!@#",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 401, res.data)

    def test_superuser_can_create_admin(self):
        self._auth_as_superuser()
        res = self.client.post(
            "/api/admin/register/",
            {
                "email": "newadmin2@example.com",
                "phone_number": "9855555555",
                "password": "AdminPass123!@#",
                "password2": "AdminPass123!@#",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        User = get_user_model()
        user = User.objects.get(email="newadmin2@example.com")
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(AdminProfile.objects.filter(user=user).exists())

    def test_superuser_can_create_staff(self):
        self._auth_as_superuser()
        res = self.client.post(
            "/api/staff/register/",
            {
                "email": "newstaff2@example.com",
                "phone_number": "9866666666",
                "password": "StaffPass123!@#",
                "password2": "StaffPass123!@#",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        User = get_user_model()
        user = User.objects.get(email="newstaff2@example.com")
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(StaffProfile.objects.filter(user=user).exists())

    def test_non_superuser_gets_403_for_public_admin_and_staff(self):
        self._auth_as_normal_user()
        res_public = self.client.post(
            "/api/register/",
            {
                "email": "blockedpublic@example.com",
                "phone_number": "9899999999",
                "password": "PublicPass123!@#",
                "password2": "PublicPass123!@#",
            },
            format="json",
        )
        self.assertEqual(res_public.status_code, 403, res_public.data)

        res_admin = self.client.post(
            "/api/admin/register/",
            {
                "email": "blockedadmin@example.com",
                "phone_number": "9877777777",
                "password": "AdminPass123!@#",
                "password2": "AdminPass123!@#",
            },
            format="json",
        )
        self.assertEqual(res_admin.status_code, 403, res_admin.data)

        res_staff = self.client.post(
            "/api/staff/register/",
            {
                "email": "blockedstaff@example.com",
                "phone_number": "9888888888",
                "password": "StaffPass123!@#",
                "password2": "StaffPass123!@#",
            },
            format="json",
        )
        self.assertEqual(res_staff.status_code, 403, res_staff.data)
