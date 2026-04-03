from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.accounts.models import AdminProfile, Designation, PublicUserProfile, StaffProfile


class RegistrationApiTests(APITestCase):
    def setUp(self):
        Designation.objects.get_or_create(name="Other", defaults={"description": ""})
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
            "/api/v1/auth/token/",
            {"email": self.superuser.email, "password": "RootPass123!@#"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def _auth_as_normal_user(self):
        res = self.client.post(
            "/api/v1/auth/token/",
            {"email": self.normal_user.email, "password": "UserPass123!@#"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_public_registration_requires_auth(self):
        res = self.client.post(
            "/api/v1/register/",
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
            "/api/v1/register/",
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
            "/api/v1/admin/register/",
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
            "/api/v1/staff/register/",
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
            "/api/v1/admin/register/",
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
            "/api/v1/staff/register/",
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
            "/api/v1/register/",
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
            "/api/v1/admin/register/",
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
            "/api/v1/staff/register/",
            {
                "email": "blockedstaff@example.com",
                "phone_number": "9888888888",
                "password": "StaffPass123!@#",
                "password2": "StaffPass123!@#",
            },
            format="json",
        )
        self.assertEqual(res_staff.status_code, 403, res_staff.data)

    def test_designations_list_requires_auth(self):
        res = self.client.get("/api/v1/admin/designations/")
        self.assertEqual(res.status_code, 401, res.data)

    def test_superuser_can_list_designations(self):
        self._auth_as_superuser()
        res = self.client.get("/api/v1/admin/designations/")
        self.assertEqual(res.status_code, 200, res.data)
        payload = res.data["results"] if isinstance(res.data, dict) and "results" in res.data else res.data
        self.assertGreaterEqual(len(payload), 1)
        row = payload[0]
        self.assertIn("id", row)
        self.assertIn("name", row)
        self.assertIn("description", row)
        self.assertTrue(Designation.objects.filter(pk=row["id"]).exists())

    def test_non_admin_user_gets_403_for_designations_list(self):
        self._auth_as_normal_user()
        res = self.client.get("/api/v1/admin/designations/")
        self.assertEqual(res.status_code, 403, res.data)

    def test_superuser_can_create_designation(self):
        self._auth_as_superuser()
        res = self.client.post(
            "/api/v1/admin/designations/",
            {"name": "Pharmacist Lead", "description": "Lead role"},
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data["name"], "Pharmacist Lead")
        self.assertTrue(Designation.objects.filter(name="Pharmacist Lead").exists())

    def test_create_designation_rejects_duplicate_name(self):
        self._auth_as_superuser()
        Designation.objects.create(name="UniqueOnce", description="")
        res = self.client.post(
            "/api/v1/admin/designations/",
            {"name": "UniqueOnce", "description": "dup"},
            format="json",
        )
        self.assertEqual(res.status_code, 400, res.data)

    def test_superuser_can_retrieve_update_patch_designation(self):
        self._auth_as_superuser()
        d = Designation.objects.create(name="Temp Role", description="old")
        url = f"/api/v1/admin/designations/{d.pk}/"

        get_res = self.client.get(url)
        self.assertEqual(get_res.status_code, 200, get_res.data)
        self.assertEqual(get_res.data["name"], "Temp Role")

        put_res = self.client.put(
            url,
            {"name": "Temp Role Renamed", "description": "new"},
            format="json",
        )
        self.assertEqual(put_res.status_code, 200, put_res.data)
        d.refresh_from_db()
        self.assertEqual(d.name, "Temp Role Renamed")

        patch_res = self.client.patch(url, {"description": "patched"}, format="json")
        self.assertEqual(patch_res.status_code, 200, patch_res.data)
        d.refresh_from_db()
        self.assertEqual(d.description, "patched")

    def test_superuser_can_delete_unused_designation(self):
        self._auth_as_superuser()
        d = Designation.objects.create(name="Orphan Role", description="")
        url = f"/api/v1/admin/designations/{d.pk}/"
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 204, res.data)
        self.assertFalse(Designation.objects.filter(pk=d.pk).exists())

    def test_cannot_delete_other_designation(self):
        self._auth_as_superuser()
        other = Designation.objects.get(name="Other")
        res = self.client.delete(f"/api/v1/admin/designations/{other.pk}/")
        self.assertEqual(res.status_code, 400, res.data)
        self.assertTrue(Designation.objects.filter(pk=other.pk).exists())

    def test_cannot_delete_designation_in_use(self):
        self._auth_as_superuser()
        d = Designation.objects.create(name="In Use Role", description="")
        User = get_user_model()
        user = User.objects.create_user(
            email="inuseadmin@example.com",
            phone_number="9777777777",
            password="XyzPass123!@#",
            is_staff=True,
            is_superuser=False,
        )
        AdminProfile.objects.create(user=user, designation=d)
        res = self.client.delete(f"/api/v1/admin/designations/{d.pk}/")
        self.assertEqual(res.status_code, 400, res.data)
        self.assertTrue(Designation.objects.filter(pk=d.pk).exists())
