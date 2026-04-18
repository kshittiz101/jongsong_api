from rest_framework import serializers

from apps.accounts.serializers import PatientUserBriefSerializer

from ..models import Medication, MedicationLog
from .patient_scope import require_homecare_patient_actor


class MedicationSerializer(serializers.ModelSerializer):
    patient_detail = PatientUserBriefSerializer(source="patient", read_only=True)

    class Meta:
        model = Medication
        fields = [
            "id",
            "patient",
            "patient_detail",
            "medication_name",
            "dosage",
            "form",
            "quantity",
            "refill_reminder",
            "start_date",
            "end_date",
            "frequency",
            "times",
            "instructions",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "patient_detail"]

    def validate_patient(self, value):
        return require_homecare_patient_actor(self.context.get("request"), value)


class MedicationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationLog
        fields = [
            "id",
            "medication",
            "scheduled_time",
            "actual_taken_time",
            "status",
            "notes",
            "marked_by",
        ]
        read_only_fields = ["id", "marked_by"]

    def validate_medication(self, med: Medication):
        request = self.context.get("request")
        if med is None:
            raise serializers.ValidationError("Medication is required.")
        require_homecare_patient_actor(
            request,
            med.patient,
            denied_message="You are not allowed to log doses for this medication.",
        )
        return med

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data.setdefault("marked_by", request.user)
        return super().create(validated_data)
