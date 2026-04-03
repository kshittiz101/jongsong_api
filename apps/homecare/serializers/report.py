from rest_framework import serializers

from apps.accounts.serializers import PatientUserBriefSerializer

from ..access import can_manage_homecare_patient
from ..models import MedicationReport


class MedicationReportSerializer(serializers.ModelSerializer):
    patient_detail = PatientUserBriefSerializer(source="patient", read_only=True)

    class Meta:
        model = MedicationReport
        fields = [
            "id",
            "patient",
            "patient_detail",
            "report_date",
            "summary",
            "recorded_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "recorded_by", "created_at", "updated_at", "patient_detail"]

    def _validate_patient_user(self, patient_user):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")
        if not can_manage_homecare_patient(request.user, patient_user):
            raise serializers.ValidationError(
                "You are not allowed to manage data for this patient."
            )
        return patient_user

    def validate_patient(self, value):
        return self._validate_patient_user(value)

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data.setdefault("recorded_by", request.user)
        return super().create(validated_data)
