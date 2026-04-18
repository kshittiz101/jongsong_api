"""
Generate persisted `PatientDailyClinicalReport` rows for all home-care patients.

Intended to run from system cron once per night after local midnight in
`settings.TIME_ZONE`, typically for "yesterday" so the calendar day is closed:

    0 1 * * * cd /path/to/jongsong_api && pipenv run python manage.py generate_homecare_daily_reports --date $(date -d yesterday +%%F)

Alternatively run without `--date` to refresh **today** (useful for staging).

Uses the same patient discovery as other home-care features: `PatientProfile`
with `patient_type=HOME_CARE`.
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import PatientProfile
from apps.homecare.services.daily_clinical_report import build_or_refresh_report
from common.constants.patient_types import PatientType

User = get_user_model()


class Command(BaseCommand):
    help = "Build or refresh daily clinical reports for every home-care patient (see module docstring for cron)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            default=None,
            help="Report calendar day as YYYY-MM-DD in settings.TIME_ZONE (default: today in that zone).",
        )

    def handle(self, *args, **options):
        raw = options["date"]
        if raw:
            target = date.fromisoformat(raw)
        else:
            target = timezone.localdate()

        user_ids = PatientProfile.objects.filter(
            patient_type=PatientType.HOME_CARE,
        ).values_list("user_id", flat=True)

        count = 0
        for uid in user_ids:
            try:
                u = User.objects.get(pk=uid)
            except User.DoesNotExist:
                continue
            build_or_refresh_report(u, target)
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Refreshed daily clinical reports for {count} patient(s) on {target}."))
