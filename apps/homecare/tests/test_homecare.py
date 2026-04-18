from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
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

from apps.homecare.models import (
    Medication,
    MedicationLog,
    PatientCaretakerAssignment,
    PatientDailyClinicalReport,
    PatientVitalReading,
)

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
            role=Role.CUSTOMER,
        )
        StaffProfile.objects.create(user=self.nurse_user, role=Role.HOME_CARE_STAFF)
        self.other_patient_user = User.objects.create_user(
            email="hcotherpat@example.com",
            phone_number="9801000005",
            password="OtherPatPass123!@#",
        )
        PublicUserProfile.objects.create(
            user=self.other_patient_user,
            role=Role.PATIENT,
        )
        PatientProfile.objects.create(
            user=self.other_patient_user,
            role=Role.PATIENT,
            patient_type=PatientType.HOME_CARE,
            date_of_birth="1992-02-02",
            blood_group=BloodGroup.A_POSITIVE,
            gender=Gender.FEMALE,
            emergency_contact_name="ec",
            emergency_contact_phone="9801000006",
            emergency_contact_relation="sister",
            home_address="Bhaktapur",
        )

    def _jwt(self, user):
        passwords = {
            self.admin_user: "AdminPass123!@#",
            self.patient_user: "PatPass123!@#",
            self.nurse_user: "NursePass123!@#",
            self.other_patient_user: "OtherPatPass123!@#",
        }
        res = self.client.post(
            "/api/v1/auth/token/",
            {"email": user.email, "password": passwords[user]},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_patient_read_only_vitals_post_forbidden_get_allowed(self):
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
        self.assertEqual(res.status_code, 400, res.data)
        res_list = self.client.get(
            "/api/v1/admin/home-care/vitals/",
            {"patient": self.patient_user.pk},
            format="json",
        )
        self.assertEqual(res_list.status_code, 200, res_list.data)

    def test_patient_cannot_patch_own_vitals(self):
        self._jwt(self.admin_user)
        ts = timezone.now()
        res = self.client.post(
            "/api/v1/admin/home-care/vitals/",
            {
                "patient": self.patient_user.pk,
                "recorded_at": ts.isoformat(),
                "heart_rate_bpm": 70,
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        vital_id = res.data["id"]
        self._jwt(self.patient_user)
        res2 = self.client.patch(
            f"/api/v1/admin/home-care/vitals/{vital_id}/",
            {"notes": "patient try"},
            format="json",
        )
        self.assertEqual(res2.status_code, 403, res2.data)

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
        self.assertEqual(res.status_code, 400, res.data)

    def test_nurse_cannot_record_vitals_for_unassigned_patient(self):
        self._jwt(self.nurse_user)
        ts = timezone.now()
        res = self.client.post(
            "/api/v1/admin/home-care/vitals/",
            {
                "patient": self.other_patient_user.pk,
                "recorded_at": ts.isoformat(),
                "heart_rate_bpm": 80,
            },
            format="json",
        )
        self.assertEqual(res.status_code, 400, res.data)

    def test_caretaker_crud_when_assigned(self):
        PatientCaretakerAssignment.objects.create(
            patient=self.patient_user,
            caretaker=self.nurse_user,
            is_active=True,
        )
        self._jwt(self.nurse_user)
        ts = timezone.now()
        res_v = self.client.post(
            "/api/v1/admin/home-care/vitals/",
            {
                "patient": self.patient_user.pk,
                "recorded_at": ts.isoformat(),
                "systolic_mmhg": 120,
                "diastolic_mmhg": 80,
            },
            format="json",
        )
        self.assertEqual(res_v.status_code, 201, res_v.data)
        vital_id = res_v.data["id"]
        res_patch = self.client.patch(
            f"/api/v1/admin/home-care/vitals/{vital_id}/",
            {"notes": "nurse note"},
            format="json",
        )
        self.assertEqual(res_patch.status_code, 200, res_patch.data)
        res_del = self.client.delete(
            f"/api/v1/admin/home-care/vitals/{vital_id}/",
            format="json",
        )
        self.assertEqual(res_del.status_code, 204, res_del.content)

        res_med = self.client.post(
            "/api/v1/admin/home-care/medications/",
            {
                "patient": self.patient_user.pk,
                "medication_name": "Aspirin",
                "dosage": "100mg",
            },
            format="json",
        )
        self.assertEqual(res_med.status_code, 201, res_med.data)
        med_id = res_med.data["id"]
        res_log = self.client.post(
            "/api/v1/admin/home-care/medication-logs/",
            {
                "medication": med_id,
                "scheduled_time": ts.isoformat(),
                "status": "taken",
            },
            format="json",
        )
        self.assertEqual(res_log.status_code, 201, res_log.data)
        log_id = res_log.data["id"]
        res_log_patch = self.client.patch(
            f"/api/v1/admin/home-care/medication-logs/{log_id}/",
            {"notes": "ok"},
            format="json",
        )
        self.assertEqual(res_log_patch.status_code, 200, res_log_patch.data)
        res_rep = self.client.post(
            "/api/v1/admin/home-care/medication-reports/",
            {
                "patient": self.patient_user.pk,
                "report_date": ts.date().isoformat(),
                "summary": "Weekly summary",
            },
            format="json",
        )
        self.assertEqual(res_rep.status_code, 201, res_rep.data)
        rep_id = res_rep.data["id"]
        res_rep_del = self.client.delete(
            f"/api/v1/admin/home-care/medication-reports/{rep_id}/",
            format="json",
        )
        self.assertEqual(res_rep_del.status_code, 204, res_rep_del.content)

    def test_caretaker_assignment_api_admin_only(self):
        url = "/api/v1/admin/home-care/caretaker-assignments/"
        self._jwt(self.admin_user)
        res = self.client.get(url, format="json")
        self.assertEqual(res.status_code, 200, res.data)
        res_c = self.client.post(
            url,
            {
                "patient": self.other_patient_user.pk,
                "caretaker": self.nurse_user.pk,
            },
            format="json",
        )
        self.assertEqual(res_c.status_code, 201, res_c.data)
        assign_id = res_c.data["id"]

        self._jwt(self.patient_user)
        self.assertEqual(self.client.get(url, format="json").status_code, 403)

        self._jwt(self.nurse_user)
        self.assertEqual(self.client.get(url, format="json").status_code, 403)

        self._jwt(self.admin_user)
        res_p = self.client.patch(
            f"{url}{assign_id}/",
            {"is_active": False},
            format="json",
        )
        self.assertEqual(res_p.status_code, 200, res_p.data)
        self.assertFalse(res_p.data["is_active"])
        self.assertIsNotNone(res_p.data.get("ended_at"))

    def test_caretaker_assignment_list_is_active_filter(self):
        """List supports ?is_active=true / false to narrow rows."""
        url = "/api/v1/admin/home-care/caretaker-assignments/"
        self._jwt(self.admin_user)
        res_c = self.client.post(
            url,
            {"patient": self.other_patient_user.pk, "caretaker": self.nurse_user.pk},
            format="json",
        )
        self.assertEqual(res_c.status_code, 201, res_c.data)
        active_id = res_c.data["id"]

        res_p = self.client.patch(
            f"{url}{active_id}/",
            {"is_active": False},
            format="json",
        )
        self.assertEqual(res_p.status_code, 200, res_p.data)

        res_c2 = self.client.post(
            url,
            {"patient": self.patient_user.pk, "caretaker": self.nurse_user.pk},
            format="json",
        )
        self.assertEqual(res_c2.status_code, 201, res_c2.data)

        res_active = self.client.get(f"{url}?is_active=true", format="json")
        self.assertEqual(res_active.status_code, 200, res_active.data)
        for row in res_active.data["results"]:
            self.assertTrue(row["is_active"])

        res_inactive = self.client.get(f"{url}?is_active=false", format="json")
        self.assertEqual(res_inactive.status_code, 200, res_inactive.data)
        inactive_ids = {row["id"] for row in res_inactive.data["results"]}
        self.assertIn(active_id, inactive_ids)

    def test_daily_clinical_report_get_upserts_and_content(self):
        """GET with patient + report_date rebuilds persisted row from logs + vitals."""
        tz = ZoneInfo(str(settings.TIME_ZONE))
        report_date = date(2026, 4, 10)
        noon = datetime.combine(report_date, time(12, 0), tzinfo=tz)

        med = Medication.objects.create(
            patient=self.patient_user,
            medication_name="TestMed",
            dosage="10mg",
            is_active=True,
        )
        MedicationLog.objects.create(
            medication=med,
            scheduled_time=noon,
            status="taken",
        )
        PatientVitalReading.objects.create(
            patient=self.patient_user,
            recorded_at=noon,
            systolic_mmhg=120,
            diastolic_mmhg=80,
            heart_rate_bpm=70,
        )

        url = "/api/v1/admin/home-care/daily-clinical-reports/"
        self._jwt(self.admin_user)
        res = self.client.get(
            url,
            {"patient": self.patient_user.pk, "report_date": report_date.isoformat()},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        results = res.data.get("results", res.data)
        self.assertEqual(len(results), 1)
        row = results[0]
        self.assertEqual(row["report_date"], report_date.isoformat())
        self.assertIn("TestMed", row["medication_summary_text"])
        self.assertIn("taken", row["medication_summary_text"])
        self.assertIn("120", row["vitals_summary_text"])
        self.assertEqual(len(row["medication_summary"]["logs"]), 1)
        self.assertEqual(len(row["vitals_summary"]["readings"]), 1)

        persisted = PatientDailyClinicalReport.objects.get(
            patient=self.patient_user,
            report_date=report_date,
        )
        self.assertEqual(persisted.id, row["id"])

    def test_daily_clinical_report_patient_can_read_own(self):
        tz = ZoneInfo(str(settings.TIME_ZONE))
        report_date = date(2026, 5, 1)
        med = Medication.objects.create(patient=self.patient_user, medication_name="A", is_active=True)
        MedicationLog.objects.create(
            medication=med,
            scheduled_time=datetime.combine(report_date, time(8, 0), tzinfo=tz),
            status="missed",
        )
        self._jwt(self.patient_user)
        res = self.client.get(
            "/api/v1/admin/home-care/daily-clinical-reports/",
            {"patient": self.patient_user.pk, "report_date": report_date.isoformat()},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(len(res.data["results"]), 1)

    def test_daily_clinical_report_nurse_forbidden_without_assignment(self):
        report_date = date(2026, 5, 2)
        self._jwt(self.nurse_user)
        res = self.client.get(
            "/api/v1/admin/home-care/daily-clinical-reports/",
            {"patient": self.patient_user.pk, "report_date": report_date.isoformat()},
            format="json",
        )
        self.assertEqual(res.status_code, 403, res.data)

    def test_daily_clinical_report_nurse_allowed_when_assigned(self):
        PatientCaretakerAssignment.objects.create(
            patient=self.patient_user,
            caretaker=self.nurse_user,
            is_active=True,
        )
        report_date = date(2026, 5, 3)
        self._jwt(self.nurse_user)
        res = self.client.get(
            "/api/v1/admin/home-care/daily-clinical-reports/",
            {"patient": self.patient_user.pk, "report_date": report_date.isoformat()},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)

    def test_daily_clinical_report_list_invalid_date_returns_400(self):
        self._jwt(self.admin_user)
        res = self.client.get(
            "/api/v1/admin/home-care/daily-clinical-reports/",
            {"patient": self.patient_user.pk, "report_date": "not-a-date"},
            format="json",
        )
        self.assertEqual(res.status_code, 400, res.data)

    def test_generate_homecare_daily_reports_command(self):
        tz = ZoneInfo(str(settings.TIME_ZONE))
        report_date = date(2026, 6, 15)
        med = Medication.objects.create(patient=self.patient_user, medication_name="CmdMed", is_active=True)
        MedicationLog.objects.create(
            medication=med,
            scheduled_time=datetime.combine(report_date, time(9, 0), tzinfo=tz),
            status="taken",
        )
        call_command("generate_homecare_daily_reports", date=report_date.isoformat())
        self.assertTrue(
            PatientDailyClinicalReport.objects.filter(
                patient=self.patient_user,
                report_date=report_date,
            ).exists()
        )
        self.assertTrue(
            PatientDailyClinicalReport.objects.filter(
                patient=self.other_patient_user,
                report_date=report_date,
            ).exists()
        )


_HC_ONBOARDING_PAYLOAD = {
    "email": "hcportalnew@example.com",
    "phone_number": "9813888888",
    "password": "PatientPass123!@#",
    "password2": "PatientPass123!@#",
    "patient_type": PatientType.HOME_CARE,
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
    """Home-care admin flows via unified patient APIs (list/filter + onboarding + patch)."""

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
        PublicUserProfile.objects.create(user=self.nurse_user, role=Role.CUSTOMER)
        StaffProfile.objects.create(user=self.nurse_user, role=Role.HOME_CARE_STAFF)

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
        res = self.client.get(
            "/api/v1/admin/patient-profiles/",
            {"patient_type": PatientType.HOME_CARE},
            format="json",
        )
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
            "/api/v1/admin/patient-profiles/",
            {"patient_type": PatientType.HOME_CARE, "phone_number": "9802000002"},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.data)
        results = res.data.get("results", res.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["user"]["id"], self.hc_patient.pk)

    def test_nurse_forbidden_list_and_create(self):
        self._jwt(self.nurse_user)
        res = self.client.get(
            "/api/v1/admin/patient-profiles/",
            {"patient_type": PatientType.HOME_CARE},
            format="json",
        )
        self.assertEqual(res.status_code, 403, res.data)
        res2 = self.client.post(
            "/api/v1/admin/patient-users/",
            _HC_ONBOARDING_PAYLOAD,
            format="json",
        )
        self.assertEqual(res2.status_code, 403, res2.data)

    def test_patient_forbidden_list(self):
        self._jwt(self.hc_patient)
        res = self.client.get(
            "/api/v1/admin/patient-profiles/",
            {"patient_type": PatientType.HOME_CARE},
            format="json",
        )
        self.assertEqual(res.status_code, 403, res.data)

    def test_admin_create_home_care_via_patient_users_onboarding(self):
        self._jwt(self.admin_user)
        res = self.client.post(
            "/api/v1/admin/patient-users/",
            _HC_ONBOARDING_PAYLOAD,
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data["patient_type"], PatientType.HOME_CARE)
        u = User.objects.get(email="hcportalnew@example.com")
        self.assertEqual(u.patient_profile.patient_type, PatientType.HOME_CARE)

    def test_admin_retrieve_and_patch(self):
        self._jwt(self.admin_user)
        hc_profile = PatientProfile.objects.get(user=self.hc_patient)
        url = f"/api/v1/admin/patient-profiles/{hc_profile.pk}/"
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
