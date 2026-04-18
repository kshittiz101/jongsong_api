from datetime import date

from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_view
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from ..access import can_view_homecare_patient
from ..models import PatientDailyClinicalReport
from ..permissions import HomeCareClinicalPermission
from ..selectors import filter_by_optional_patient_param, get_daily_clinical_reports_queryset
from ..serializers import PatientDailyClinicalReportSerializer
from ..services.daily_clinical_report import build_or_refresh_report

from .schema import HOMECARE_DAILY_CLINICAL_SCHEMA

User = get_user_model()


@extend_schema_view(**HOMECARE_DAILY_CLINICAL_SCHEMA)
class PatientDailyClinicalReportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only combined daily report. GET list with `patient` and `report_date`
    recomputes and upserts the row from medications/vitals before responding.
    """

    permission_classes = [HomeCareClinicalPermission]
    serializer_class = PatientDailyClinicalReportSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ("report_date", "id")
    ordering = ("-report_date",)

    def get_queryset(self):
        user = self.request.user
        qs = get_daily_clinical_reports_queryset(user)
        if self.action == "list" and not self.request.query_params.get("patient"):
            return PatientDailyClinicalReport.objects.none()
        qs = filter_by_optional_patient_param(qs, self.request, user, "patient_id")
        rd = self.request.query_params.get("report_date")
        if rd:
            try:
                d = date.fromisoformat(rd)
            except ValueError:
                return PatientDailyClinicalReport.objects.none()
            qs = qs.filter(report_date=d)
        return qs

    def list(self, request, *args, **kwargs):
        patient_raw = request.query_params.get("patient")
        date_raw = request.query_params.get("report_date")
        if patient_raw and date_raw:
            try:
                pid = int(patient_raw)
                rd = date.fromisoformat(date_raw)
            except (ValueError, TypeError):
                return Response(
                    {"detail": "Invalid patient or report_date (use YYYY-MM-DD)."},
                    status=400,
                )
            try:
                patient_user = User.objects.get(pk=pid)
            except User.DoesNotExist:
                return Response({"detail": "Patient not found."}, status=404)
            if not can_view_homecare_patient(request.user, patient_user):
                return Response(status=403)
            build_or_refresh_report(patient_user, rd)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        build_or_refresh_report(instance.patient, instance.report_date)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
