from rest_framework import serializers

from apps.accounts.serializers import PatientUserBriefSerializer

from ..models import PatientVitalReading
from .patient_scope import require_homecare_patient_actor


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

    def validate_patient(self, value):
        return require_homecare_patient_actor(self.context.get("request"), value)

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data.setdefault("recorded_by", request.user)
        return super().create(validated_data)
