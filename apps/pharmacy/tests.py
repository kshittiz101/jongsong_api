import io

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APITestCase

from apps.accounts.models import Designation, StaffProfile
from common.constants.roles import Role

from .models import Prescription

User = get_user_model()


class PrescriptionAPITests(APITestCase):
    """Test suite for Prescription API endpoints covering permissions and CRUD operations."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_designation, _ = Designation.objects.get_or_create(
            name="Other",
            defaults={"description": "Default designation"},
        )
        cls.pharmacist_designation, _ = Designation.objects.get_or_create(
            name="Pharmacist",
            defaults={"description": "Licensed Pharmacist"},
        )

    def setUp(self):
        # Create superuser
        self.superuser = User.objects.create_superuser(
            email="root@example.com",
            phone_number="9800000000",
            password="RootPass123!@#",
        )

        # Create staff user with Other designation (non-pharmacist)
        self.staff_user = User.objects.create_user(
            email="staff@example.com",
            phone_number="9811111111",
            password="StaffPass123!@#",
            is_staff=True,
        )
        self.staff_profile = StaffProfile.objects.create(
            user=self.staff_user,
            role=Role.PHARMACY_STAFF,
            designation=self.other_designation,
        )

        # Create pharmacist user
        self.pharmacist_user = User.objects.create_user(
            email="pharmacist@example.com",
            phone_number="9822222222",
            password="PharmPass123!@#",
            is_staff=True,
        )
        self.pharmacist_profile = StaffProfile.objects.create(
            user=self.pharmacist_user,
            role=Role.PHARMACY_STAFF,
            designation=self.pharmacist_designation,
        )

        # Create a test prescription
        self.prescription = Prescription.objects.create(
            full_name="Test Patient",
            phone_number="9876543210",
            prescription_notes="Take twice daily",
            status="pending",
        )

    def _get_test_image(self):
        """Create a valid test image file."""
        # Create a valid 1x1 red pixel PNG image
        file = io.BytesIO()
        image = Image.new('RGB', (1, 1), color='red')
        image.save(file, 'PNG')
        file.seek(0)
        return SimpleUploadedFile(
            name="test_prescription.png",
            content=file.read(),
            content_type="image/png",
        )

    def _auth_as_superuser(self):
        """Authenticate as superuser."""
        res = self.client.post(
            "/api/v1/auth/token/",
            {"email": self.superuser.email, "password": "RootPass123!@#"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def _auth_as_pharmacist(self):
        """Authenticate as pharmacist."""
        res = self.client.post(
            "/api/v1/auth/token/",
            {"email": self.pharmacist_user.email, "password": "PharmPass123!@#"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def _auth_as_staff(self):
        """Authenticate as regular staff."""
        res = self.client.post(
            "/api/v1/auth/token/",
            {"email": self.staff_user.email, "password": "StaffPass123!@#"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    # ─────────────────────────────────────────────────────────────────────────────
    # Test: Unauthenticated users can create prescriptions
    # ─────────────────────────────────────────────────────────────────────────────

    def test_unauthenticated_user_can_create_prescription(self):
        """Unauthenticated user can create a prescription (status defaults to pending)."""
        image = self._get_test_image()
        res = self.client.post(
            "/api/v1/prescriptions/",
            {
                "prescription_img": image,
                "full_name": "John Doe",
                "phone_number": "9876543210",
                "prescription_notes": "Test notes",
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data["full_name"], "John Doe")
        self.assertEqual(res.data["status"], "pending")

    def test_unauthenticated_user_can_list_prescriptions(self):
        """Unauthenticated user can list prescriptions."""
        res = self.client.get("/api/v1/prescriptions/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("results", res.data)

    def test_unauthenticated_user_can_retrieve_prescription(self):
        """Unauthenticated user can retrieve a prescription by ID."""
        res = self.client.get(
            f"/api/v1/prescriptions/{self.prescription.pk}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["full_name"], "Test Patient")

    # ─────────────────────────────────────────────────────────────────────────────
    # Test: Status field protection for unauthenticated users
    # ─────────────────────────────────────────────────────────────────────────────

    def test_unauthenticated_user_cannot_update_status(self):
        """Unauthenticated user cannot update status field (gets 401 for unauthenticated)."""
        res = self.client.patch(
            f"/api/v1/prescriptions/{self.prescription.pk}/",
            {"status": "processing"},
            format="json",
        )
        # DRF returns 401 for unauthenticated users when permission denied
        self.assertEqual(res.status_code, 401, res.data)

    # ─────────────────────────────────────────────────────────────────────────────
    # Test: Non-pharmacist staff cannot update status
    # ─────────────────────────────────────────────────────────────────────────────

    def test_non_pharmacist_staff_cannot_update_status(self):
        """Staff with non-Pharmacist designation cannot update status."""
        self._auth_as_staff()
        res = self.client.patch(
            f"/api/v1/prescriptions/{self.prescription.pk}/",
            {"status": "processing"},
            format="json",
        )
        self.assertEqual(res.status_code, 403, res.data)

    def test_non_pharmacist_can_update_other_fields(self):
        """Non-pharmacist staff can update non-status fields."""
        self._auth_as_staff()
        res = self.client.patch(
            f"/api/v1/prescriptions/{self.prescription.pk}/",
            {"prescription_notes": "Updated notes"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data["prescription_notes"], "Updated notes")

    # ─────────────────────────────────────────────────────────────────────────────
    # Test: Pharmacist can update status
    # ─────────────────────────────────────────────────────────────────────────────

    def test_pharmacist_can_update_status(self):
        """Staff with Pharmacist designation can update status."""
        self._auth_as_pharmacist()
        res = self.client.patch(
            f"/api/v1/prescriptions/{self.prescription.pk}/",
            {"status": "processing"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data["status"], "processing")

    def test_pharmacist_can_update_status_to_completed(self):
        """Pharmacist can update status to completed."""
        self._auth_as_pharmacist()
        res = self.client.patch(
            f"/api/v1/prescriptions/{self.prescription.pk}/",
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data["status"], "completed")

    # ─────────────────────────────────────────────────────────────────────────────
    # Test: Superuser can update status
    # ─────────────────────────────────────────────────────────────────────────────

    def test_superuser_can_update_status(self):
        """Superuser can update prescription status."""
        self._auth_as_superuser()
        res = self.client.patch(
            f"/api/v1/prescriptions/{self.prescription.pk}/",
            {"status": "processing"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data["status"], "processing")

    # ─────────────────────────────────────────────────────────────────────────────
    # Test: Delete permissions
    # ─────────────────────────────────────────────────────────────────────────────

    def test_unauthenticated_user_can_delete_prescription(self):
        """Unauthenticated user can delete a prescription."""
        res = self.client.delete(
            f"/api/v1/prescriptions/{self.prescription.pk}/"
        )
        self.assertEqual(res.status_code, 204)
        self.assertFalse(
            Prescription.objects.filter(pk=self.prescription.pk).exists()
        )
