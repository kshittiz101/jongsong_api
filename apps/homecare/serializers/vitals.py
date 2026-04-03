from rest_framework import serializers

from apps.accounts.serializers import PatientUserBriefSerializer

from ..access import can_manage_homecare_patient
from ..models import PatientVitalReading


class PatientVitalReadingSerializer(serializers.ModelSerializer):
    patient_detail = PatientUserBriefSerializer(source="patient", read_only=True)

    class Meta:
        model = PatientVitalReading
        fields = [
            "id",
            "patient",
            "patient_detail",
            "recorded_at",
            "recorded_by",
            "systolic_mmhg",
            "diastolic_mmhg",
            "heart_rate_bpm",
            "temperature_celsius",
            "spo2_percent",
            "respiratory_rate",
            "blood_glucose_mg_dl",
            "weight_kg",
            "height_cm",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "recorded_by", "created_at", "patient_detail"]

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
