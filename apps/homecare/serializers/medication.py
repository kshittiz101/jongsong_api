from rest_framework import serializers

from apps.accounts.serializers import PatientUserBriefSerializer

from ..access import can_manage_homecare_patient
from ..models import Medication, MedicationLog


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
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")
        if med is None:
            raise serializers.ValidationError("Medication is required.")
        if not can_manage_homecare_patient(request.user, med.patient):
            raise serializers.ValidationError(
                "You are not allowed to log doses for this medication."
            )
        return med

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data.setdefault("marked_by", request.user)
        return super().create(validated_data)
