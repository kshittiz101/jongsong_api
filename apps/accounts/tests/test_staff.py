from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.accounts.models import AdminProfile, Designation, StaffProfile
from common.constants.roles import Role


User = get_user_model()


class StaffManagementApiTests(APITestCase):
    """Test suite for Staff Management API endpoints covering permissions, CRUD, pagination, search, and soft-delete."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Ensure "Other" designation exists for tests
        cls.other_designation, _ = Designation.objects.get_or_create(
            name="Other",
            defaults={"description": "Default designation"},
        )

    def setUp(self):
        # Create superuser
        self.superuser = User.objects.create_superuser(
            email="root@example.com",
            phone_number="9800000000",
            password="RootPass123!@#",
        )

        # Create normal user (no staff/admin profile)
        self.normal_user = User.objects.create_user(
            email="user@example.com",
            phone_number="9811111111",
            password="UserPass123!@#",
            is_staff=False,
            is_superuser=False,
        )

        # Create staff user (has StaffProfile)
        self.staff_user = User.objects.create_user(
            email="staff@example.com",
            phone_number="9822222222",
            password="StaffPass123!@#",
            is_staff=True,
            is_superuser=False,
        )
        self.staff_profile = StaffProfile.objects.create(
            user=self.staff_user,
            role=Role.PHARMACY_STAFF,
            designation=self.other_designation,
        )

        # Create admin user (has AdminProfile)
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            phone_number="9833333333",
            password="AdminPass123!@#",
            is_staff=True,
            is_superuser=False,
        )
        self.admin_profile = AdminProfile.objects.create(
            user=self.admin_user,
            role=Role.ADMIN,
            designation=self.other_designation,
        )

    def _auth_as_superuser(self):
        """Authenticate as superuser and set Bearer token."""
        res = self.client.post(
            "/api/v1/auth/token/",
            {"email": self.superuser.email, "password": "RootPass123!@#"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def _auth_as_normal_user(self):
        """Authenticate as normal user and set Bearer token."""
        res = self.client.post(
            "/api/v1/auth/token/",
            {"email": self.normal_user.email, "password": "UserPass123!@#"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def _auth_as_staff_user(self):
        """Authenticate as staff user and set Bearer token."""
        res = self.client.post(
            "/api/v1/auth/token/",
            {"email": self.staff_user.email, "password": "StaffPass123!@#"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def _auth_as_admin_user(self):
        """Authenticate as admin user and set Bearer token."""
        res = self.client.post(
            "/api/v1/auth/token/",
            {"email": self.admin_user.email, "password": "AdminPass123!@#"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    # ─────────────────────────────────────────────────────────────────────────────
    # PERM-01: Permission tests for non-admin users
    # ─────────────────────────────────────────────────────────────────────────────

    def test_non_admin_forbidden_list_create_update_delete(self):
        """Normal user (no admin/staff profile) gets 403 on all staff management endpoints."""
        self._auth_as_normal_user()

        # List
        res = self.client.get("/api/v1/admin/staff/")
        self.assertEqual(res.status_code, 403, res.data)

        # Create
        res = self.client.post(
            "/api/v1/admin/staff/",
            {
                "email": "newstaff@example.com",
                "phone_number": "9844444444",
                "password": "StaffPass123!@#",
                "password2": "StaffPass123!@#",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 403, res.data)

        # Update (PATCH on existing staff user)
        res = self.client.patch(
            f"/api/v1/admin/staff/{self.staff_user.pk}/",
            {"first_name": "Updated"},
            format="json",
        )
        self.assertEqual(res.status_code, 403, res.data)

        # Delete
        res = self.client.delete(f"/api/v1/admin/staff/{self.staff_user.pk}/")
        self.assertEqual(res.status_code, 403, res.data)

    def test_staff_user_forbidden(self):
        """Staff user (has StaffProfile) gets 403 on staff management endpoints."""
        self._auth_as_staff_user()

        # List
        res = self.client.get("/api/v1/admin/staff/")
        self.assertEqual(res.status_code, 403, res.data)

        # Create
        res = self.client.post(
            "/api/v1/admin/staff/",
            {
                "email": "anotherstaff@example.com",
                "phone_number": "9855555555",
                "password": "StaffPass123!@#",
                "password2": "StaffPass123!@#",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 403, res.data)

        # Update
        res = self.client.patch(
            f"/api/v1/admin/staff/{self.staff_user.pk}/",
            {"first_name": "Updated"},
            format="json",
        )
        self.assertEqual(res.status_code, 403, res.data)

        # Delete
        res = self.client.delete(f"/api/v1/admin/staff/{self.staff_user.pk}/")
        self.assertEqual(res.status_code, 403, res.data)

    # ─────────────────────────────────────────────────────────────────────────────
    # STAF-01: Admin can create staff user
    # ─────────────────────────────────────────────────────────────────────────────

    def test_superuser_can_create_staff_user(self):
        """Superuser can create a staff user via POST and StaffProfile is created with role=PHARMACY_STAFF."""
        self._auth_as_superuser()

        res = self.client.post(
            "/api/v1/admin/staff/",
            {
                "email": "newstaff@example.com",
                "phone_number": "9866666666",
                "password": "StaffPass123!@#",
                "password2": "StaffPass123!@#",
                "first_name": "New",
                "last_name": "Staff",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)

        # Verify user exists
        user = User.objects.get(email="newstaff@example.com")
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

        # Verify StaffProfile exists with correct role
        self.assertTrue(StaffProfile.objects.filter(user=user).exists())
        staff_profile = StaffProfile.objects.get(user=user)
        self.assertEqual(staff_profile.role, Role.PHARMACY_STAFF)

    def test_admin_with_admin_profile_can_create_staff_user(self):
        """Admin user (has AdminProfile) can create a staff user."""
        self._auth_as_admin_user()

        res = self.client.post(
            "/api/v1/admin/staff/",
            {
                "email": "admincreated@example.com",
                "phone_number": "9877777777",
                "password": "StaffPass123!@#",
                "password2": "StaffPass123!@#",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)

        user = User.objects.get(email="admincreated@example.com")
        self.assertTrue(StaffProfile.objects.filter(user=user).exists())

    # ─────────────────────────────────────────────────────────────────────────────
    # STAF-02/STAF-06: List pagination, search, and is_active filter
    # ─────────────────────────────────────────────────────────────────────────────

    def test_list_pagination_shape(self):
        """List endpoint returns paginated shape with count, next, previous, results."""
        self._auth_as_superuser()

        res = self.client.get("/api/v1/admin/staff/")
        self.assertEqual(res.status_code, 200, res.data)

        # Check pagination keys
        self.assertIn("count", res.data)
        self.assertIn("next", res.data)
        self.assertIn("previous", res.data)
        self.assertIn("results", res.data)
        self.assertIsInstance(res.data["results"], list)

    def test_list_search_filter(self):
        """List endpoint supports ?search= parameter."""
        self._auth_as_superuser()

        # Create additional staff user for search testing
        another_staff = User.objects.create_user(
            email="searchtest@example.com",
            phone_number="9888888888",
            password="StaffPass123!@#",
            is_staff=True,
            is_superuser=False,
        )
        StaffProfile.objects.create(
            user=another_staff,
            role=Role.PHARMACY_STAFF,
            designation=self.other_designation,
        )

        # Search by email fragment
        res = self.client.get("/api/v1/admin/staff/?search=searchtest")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertGreaterEqual(res.data["count"], 1)

        # Verify result contains the searched user
        emails = [r["email"] for r in res.data["results"]]
        self.assertIn("searchtest@example.com", emails)

    def test_list_is_active_filter(self):
        """List endpoint supports ?is_active= filter."""
        self._auth_as_superuser()

        # Create an inactive staff user
        inactive_staff = User.objects.create_user(
            email="inactive@example.com",
            phone_number="9899999999",
            password="StaffPass123!@#",
            is_staff=True,
            is_superuser=False,
            is_active=False,
        )
        StaffProfile.objects.create(
            user=inactive_staff,
            role=Role.PHARMACY_STAFF,
            designation=self.other_designation,
        )

        # Filter for active only
        res = self.client.get("/api/v1/admin/staff/?is_active=true")
        self.assertEqual(res.status_code, 200, res.data)
        for result in res.data["results"]:
            self.assertTrue(result["is_active"])

        # Filter for inactive only
        res = self.client.get("/api/v1/admin/staff/?is_active=false")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertGreaterEqual(res.data["count"], 1)
        for result in res.data["results"]:
            self.assertFalse(result["is_active"])

    def test_list_role_filter_home_care_staff(self):
        """List supports ?role=home_care_staff to restrict to that staff profile role."""
        self._auth_as_superuser()

        hc_user = User.objects.create_user(
            email="hcstaffonly@example.com",
            phone_number="9922222222",
            password="StaffPass123!@#",
            is_staff=True,
            is_superuser=False,
        )
        StaffProfile.objects.create(
            user=hc_user,
            role=Role.HOME_CARE_STAFF,
            designation=self.other_designation,
        )

        res = self.client.get("/api/v1/admin/staff/?role=home_care_staff")
        self.assertEqual(res.status_code, 200, res.data)
        ids = [r["id"] for r in res.data["results"]]
        self.assertIn(hc_user.pk, ids)
        self.assertNotIn(self.staff_user.pk, ids)

        res_all = self.client.get("/api/v1/admin/staff/?role=pharmacy_staff")
        self.assertEqual(res_all.status_code, 200, res.data)
        ids_ph = [r["id"] for r in res_all.data["results"]]
        self.assertIn(self.staff_user.pk, ids_ph)
        self.assertNotIn(hc_user.pk, ids_ph)

    def test_list_role_invalid_returns_empty(self):
        """Unknown ?role= value yields an empty result set (strict filter)."""
        self._auth_as_superuser()
        res = self.client.get("/api/v1/admin/staff/?role=not_a_real_role")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data["count"], 0)
        self.assertEqual(len(res.data["results"]), 0)

    # ─────────────────────────────────────────────────────────────────────────────
    # STAF-03: Retrieve works for staff user id
    # ─────────────────────────────────────────────────────────────────────────────

    def test_retrieve_staff_user(self):
        """Admin can retrieve a staff user by ID."""
        self._auth_as_superuser()

        res = self.client.get(f"/api/v1/admin/staff/{self.staff_user.pk}/")
        self.assertEqual(res.status_code, 200, res.data)

        self.assertEqual(res.data["email"], self.staff_user.email)
        self.assertEqual(res.data["id"], self.staff_user.pk)
        self.assertIn("staff_profile", res.data)

    # ─────────────────────────────────────────────────────────────────────────────
    # STAF-04/PERM-02: Privilege escalation safeguards
    # ─────────────────────────────────────────────────────────────────────────────

    def test_update_rejects_is_superuser_field(self):
        """Update rejects attempts to set is_superuser via PATCH."""
        self._auth_as_superuser()

        res = self.client.patch(
            f"/api/v1/admin/staff/{self.staff_user.pk}/",
            {"is_superuser": True},
            format="json",
        )
        # Should either reject with 400 or silently ignore
        # Based on serializer, it should raise validation error for unknown/forbidden fields
        self.assertEqual(res.status_code, 400, res.data)

        # Verify DB was not changed
        self.staff_user.refresh_from_db()
        self.assertFalse(self.staff_user.is_superuser)

    def test_update_rejects_is_staff_field(self):
        """Update rejects attempts to set is_staff via PATCH."""
        self._auth_as_superuser()

        res = self.client.patch(
            f"/api/v1/admin/staff/{self.staff_user.pk}/",
            {"is_staff": False},
            format="json",
        )
        self.assertEqual(res.status_code, 400, res.data)

        self.staff_user.refresh_from_db()
        self.assertTrue(self.staff_user.is_staff)

    def test_update_profile_role_field(self):
        """Admin can PATCH staff profile role (StaffProfile.role)."""
        self._auth_as_superuser()

        res = self.client.patch(
            f"/api/v1/admin/staff/{self.staff_user.pk}/",
            {"role": Role.ADMIN},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)

        self.staff_profile.refresh_from_db()
        self.assertEqual(self.staff_profile.role, Role.ADMIN)

    def test_create_staff_with_profile_details(self):
        """POST can set StaffProfile text/numeric fields alongside the user."""
        self._auth_as_superuser()

        res = self.client.post(
            "/api/v1/admin/staff/",
            {
                "email": "fullprofile@example.com",
                "phone_number": "9911223344",
                "password": "StaffPass123!@#",
                "password2": "StaffPass123!@#",
                "first_name": "Full",
                "last_name": "Profile",
                "address": "Kathmandu",
                "highest_degree": "MBBS",
                "field_of_study": "General Medicine",
                "university": "TU",
                "graduation_year": 2018,
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)

        user = User.objects.get(email="fullprofile@example.com")
        profile = StaffProfile.objects.get(user=user)
        self.assertEqual(profile.address, "Kathmandu")
        self.assertEqual(profile.highest_degree, "MBBS")
        self.assertEqual(profile.field_of_study, "General Medicine")
        self.assertEqual(profile.university, "TU")
        self.assertEqual(profile.graduation_year, 2018)

    def test_update_staff_profile_text_fields(self):
        """PATCH can update staff profile extended fields."""
        self._auth_as_superuser()

        res = self.client.patch(
            f"/api/v1/admin/staff/{self.staff_user.pk}/",
            {
                "address": "Pokhara",
                "highest_degree": "MD",
                "graduation_year": 2020,
            },
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)

        self.staff_profile.refresh_from_db()
        self.assertEqual(self.staff_profile.address, "Pokhara")
        self.assertEqual(self.staff_profile.highest_degree, "MD")
        self.assertEqual(self.staff_profile.graduation_year, 2020)

    def test_update_allowed_fields(self):
        """Update allows modifying permitted fields like first_name, last_name."""
        self._auth_as_superuser()

        res = self.client.patch(
            f"/api/v1/admin/staff/{self.staff_user.pk}/",
            {"first_name": "Updated", "last_name": "Name"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)

        self.staff_user.refresh_from_db()
        self.assertEqual(self.staff_user.first_name, "Updated")
        self.assertEqual(self.staff_user.last_name, "Name")

    # ─────────────────────────────────────────────────────────────────────────────
    # STAF-05: Delete deactivates (soft delete)
    # ─────────────────────────────────────────────────────────────────────────────

    def test_delete_deactivates_user(self):
        """DELETE on staff user sets is_active=False and returns 204."""
        self._auth_as_superuser()

        # Ensure user is active before delete
        self.assertTrue(self.staff_user.is_active)

        res = self.client.delete(f"/api/v1/admin/staff/{self.staff_user.pk}/")
        self.assertEqual(res.status_code, 204, res.data)

        # Verify user is deactivated
        self.staff_user.refresh_from_db()
        self.assertFalse(self.staff_user.is_active)

    def test_deactivated_user_excluded_from_active_filter(self):
        """Deactivated users do not appear when is_active=true filter is used."""
        self._auth_as_superuser()

        # Deactivate the staff user
        res = self.client.delete(f"/api/v1/admin/staff/{self.staff_user.pk}/")
        self.assertEqual(res.status_code, 204)

        # Query active staff
        res = self.client.get("/api/v1/admin/staff/?is_active=true")
        self.assertEqual(res.status_code, 200, res.data)

        # Ensure deactivated user is not in results
        ids = [r["id"] for r in res.data["results"]]
        self.assertNotIn(self.staff_user.pk, ids)

    def test_deactivated_user_appears_in_inactive_filter(self):
        """Deactivated users appear when is_active=false filter is used."""
        self._auth_as_superuser()

        # Deactivate the staff user
        res = self.client.delete(f"/api/v1/admin/staff/{self.staff_user.pk}/")
        self.assertEqual(res.status_code, 204)

        # Query inactive staff
        res = self.client.get("/api/v1/admin/staff/?is_active=false")
        self.assertEqual(res.status_code, 200, res.data)

        # Ensure deactivated user is in results
        ids = [r["id"] for r in res.data["results"]]
        self.assertIn(self.staff_user.pk, ids)
