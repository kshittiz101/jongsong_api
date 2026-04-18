from rest_framework import serializers

from apps.accounts.serializers import PatientUserBriefSerializer

from ..models import PatientDailyClinicalReport


class PatientDailyClinicalReportSerializer(serializers.ModelSerializer):
    patient_detail = PatientUserBriefSerializer(source="patient", read_only=True)

    class Meta:
        model = PatientDailyClinicalReport
        fields = [
            "id",
            "patient",
            "patient_detail",
            "report_date",
            "medication_summary",
            "medication_summary_text",
            "vitals_summary",
            "vitals_summary_text",
            "generated_at",
        ]
        read_only_fields = fields
