from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.accounts.serializers import PatientUserBriefSerializer

from ..access import patient_users_with_profile_queryset
from ..models import PatientCareAssignment


class StaffUserPrimaryKeyField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        from django.contrib.auth import get_user_model
        return get_user_model().objects.filter(staff_profile__isnull=False)


class PatientCareAssignmentSerializer(serializers.ModelSerializer):
    patient_detail = PatientUserBriefSerializer(source="patient", read_only=True)

    class Meta:
        model = PatientCareAssignment
        fields = [
            "id",
            "patient",
            "patient_detail",
            "doctor",
            "nurse",
            "is_active",
            "assigned_at",
            "ended_at",
            "notes",
        ]
        read_only_fields = ["id", "assigned_at", "patient_detail"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["patient"] = serializers.PrimaryKeyRelatedField(
            queryset=patient_users_with_profile_queryset()
        )
        self.fields["doctor"] = StaffUserPrimaryKeyField(allow_null=True, required=False)
        self.fields["nurse"] = StaffUserPrimaryKeyField(allow_null=True, required=False)

    def validate(self, attrs):
        instance = self.instance
        doctor = attrs.get("doctor", instance.doctor if instance else None)
        nurse = attrs.get("nurse", instance.nurse if instance else None)
        is_active = attrs.get(
            "is_active", instance.is_active if instance else True
        )

        if is_active and doctor is None and nurse is None:
            raise serializers.ValidationError(
                "Assign at least a doctor or a nurse for an active assignment."
            )
        if doctor is not None and nurse is not None and doctor.id == nurse.id:
            raise serializers.ValidationError(
                {"nurse": "Doctor and nurse must be different users."}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        patient = validated_data["patient"]
        if validated_data.get("is_active", True):
            PatientCareAssignment.objects.filter(
                patient=patient, is_active=True
            ).update(is_active=False, ended_at=timezone.now())
        try:
            return super().create(validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from exc

    @transaction.atomic
    def update(self, instance, validated_data):
        becoming_active = validated_data.get("is_active", instance.is_active)
        if becoming_active and not instance.is_active:
            PatientCareAssignment.objects.filter(
                patient_id=instance.patient_id, is_active=True
            ).exclude(pk=instance.pk).update(
                is_active=False, ended_at=timezone.now()
            )
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from exc
        instance.save()
        return instance
