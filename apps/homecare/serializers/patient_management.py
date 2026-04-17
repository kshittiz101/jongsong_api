"""Serializers for admin home-care patient portal (create / update)."""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from apps.accounts.serializers.patient import PatientUserOnboardingSerializer
from apps.accounts.models import PatientProfile
from common.constants.patient_types import PatientType

User = get_user_model()

_PROFILE_PATCHABLE = (
    "date_of_birth",
    "blood_group",
    "gender",
    "emergency_contact_name",
    "emergency_contact_phone",
    "emergency_contact_relation",
    "chronic_conditions",
    "allergies",
    "previous_surgeries",
    "family_history",
    "home_address",
    "preferred_care_time",
    "special_instructions",
    "requires_24h_care",
    "is_active_patient",
    "discharge_date",
)


class HomeCarePatientCreateSerializer(PatientUserOnboardingSerializer):
    """
    Same as patient onboarding but `patient_type` is always home_care (not accepted from client).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("patient_type", None)

    @transaction.atomic
    def create(self, validated_data):
        validated_data["patient_type"] = PatientType.HOME_CARE
        return super().create(validated_data)


class HomeCarePatientUpdateSerializer(serializers.Serializer):
    """Partial update of linked user + PatientProfile for a home-care patient."""

    first_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(max_length=100, required=False)

    date_of_birth = serializers.DateField(required=False, allow_null=True)
    blood_group = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    gender = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    emergency_contact_name = serializers.CharField(
        max_length=100, required=False, allow_blank=True, allow_null=True
    )
    emergency_contact_phone = serializers.CharField(
        max_length=100, required=False, allow_blank=True, allow_null=True
    )
    emergency_contact_relation = serializers.CharField(
        max_length=50, required=False, allow_blank=True, allow_null=True
    )
    chronic_conditions = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    allergies = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    previous_surgeries = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    family_history = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    home_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    preferred_care_time = serializers.CharField(
        max_length=100, required=False, allow_blank=True, allow_null=True
    )
    special_instructions = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    requires_24h_care = serializers.BooleanField(required=False, allow_null=True)
    is_active_patient = serializers.BooleanField(required=False, allow_null=True)
    discharge_date = serializers.DateTimeField(required=False, allow_null=True)

    def validate_email(self, value):
        user = self.context["user"]
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_phone_number(self, value):
        user = self.context["user"]
        if User.objects.exclude(pk=user.pk).filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already in use.")
        return value

    def validate(self, attrs):
        discharge = attrs.get("discharge_date")
        if discharge is None and "discharge_date" not in attrs:
            return attrs
        profile: PatientProfile = self.context["profile"]
        admission = profile.admission_date
        if discharge and admission and discharge.date() < admission.date():
            raise serializers.ValidationError(
                {"discharge_date": "Discharge date cannot be before admission date."}
            )
        return attrs

    @transaction.atomic
    def update(self, profile: PatientProfile, validated_data):
        user = profile.user
        for key in ("first_name", "last_name", "email", "phone_number"):
            if key in validated_data:
                setattr(user, key, validated_data[key])
        if any(k in validated_data for k in ("first_name", "last_name", "email", "phone_number")):
            user.save()

        for key in _PROFILE_PATCHABLE:
            if key in validated_data:
                setattr(profile, key, validated_data[key])
        if any(k in validated_data for k in _PROFILE_PATCHABLE):
            try:
                profile.full_clean()
            except DjangoValidationError as exc:
                raise serializers.ValidationError(exc.message_dict) from exc
            profile.save()
        return profile
