from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from common.constants.blood_groups import BloodGroup
from common.constants.genders import Gender
from common.constants.patient_types import PatientType
from common.constants.roles import Role

from ..models import CustomUser, PatientProfile, PublicUserProfile

User = get_user_model()


def _validate_patient_profile_role(value):
    if value != Role.PATIENT:
        raise serializers.ValidationError(
            "Only the patient role is allowed for patient profiles."
        )
    return value


class PatientUserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "phone_number", "first_name", "last_name"]
        read_only_fields = fields


def _eligible_patient_user_queryset():
    return User.objects.filter(
        publicuserprofile__role=Role.PATIENT,
        patient_profile__isnull=True,
    )


class PatientProfileSerializer(serializers.ModelSerializer):
    user = PatientUserBriefSerializer(read_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            "id",
            "user",
            "role",
            "unique_health_id",
            "patient_type",
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
            "admission_date",
            "discharge_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "role",
            "unique_health_id",
            "admission_date",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        instance = self.instance
        if instance is None:
            return attrs
        discharge = attrs.get("discharge_date", instance.discharge_date)
        admission = attrs.get("admission_date", instance.admission_date)
        if discharge and admission and discharge.date() < admission.date():
            raise serializers.ValidationError(
                {
                    "discharge_date": (
                        "Discharge date cannot be before admission date."
                    )
                }
            )
        return attrs

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict) from exc
        instance.save()
        return instance


class PatientProfileAdminCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=_eligible_patient_user_queryset()
    )
    role = serializers.ChoiceField(
        choices=Role.choices,
        default=Role.PATIENT,
    )

    class Meta:
        model = PatientProfile
        fields = [
            "id",
            "user",
            "role",
            "patient_type",
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
        ]
        read_only_fields = ["id"]

    def validate_role(self, value):
        return _validate_patient_profile_role(value)

    def validate_user(self, value):
        if not hasattr(value, "publicuserprofile"):
            raise serializers.ValidationError(
                "User must have a public profile."
            )
        if value.publicuserprofile.role != Role.PATIENT:
            raise serializers.ValidationError(
                "User public profile role must be patient to attach "
                "a patient profile."
            )
        if PatientProfile.objects.filter(user=value).exists():
            raise serializers.ValidationError(
                "This user already has a patient profile."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        profile = PatientProfile(**validated_data)
        profile.save()
        return profile


class PatientUserOnboardingSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    phone_number = serializers.CharField(
        max_length=100,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())],
    )
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        label="Confirm password",
    )
    first_name = serializers.CharField(
        max_length=150,
        trim_whitespace=True,
        required=False,
        allow_blank=True,
        default="",
    )
    last_name = serializers.CharField(
        max_length=150,
        trim_whitespace=True,
        required=False,
        allow_blank=True,
        default="",
    )

    patient_type = serializers.ChoiceField(choices=PatientType.choices)
    date_of_birth = serializers.DateField()
    blood_group = serializers.ChoiceField(choices=BloodGroup.choices)
    gender = serializers.ChoiceField(choices=Gender.choices)
    emergency_contact_name = serializers.CharField(max_length=100)
    emergency_contact_phone = serializers.CharField(max_length=100)
    emergency_contact_relation = serializers.CharField(max_length=50)
    chronic_conditions = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    allergies = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )
    previous_surgeries = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    family_history = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )
    home_address = serializers.CharField()
    preferred_care_time = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        default="",
    )
    special_instructions = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    requires_24h_care = serializers.BooleanField(required=False, default=False)
    is_active_patient = serializers.BooleanField(required=False, default=True)
    role = serializers.ChoiceField(
        choices=Role.choices,
        default=Role.PATIENT,
        help_text="Must be patient for home-care onboarding.",
    )

    def validate_role(self, value):
        return _validate_patient_profile_role(value)

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "Passwords do not match."}
            )
        try:
            validate_password(password=attrs["password"])
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("password2", None)
        password = validated_data.pop("password")
        email = validated_data.pop("email")
        phone_number = validated_data.pop("phone_number")
        first_name = validated_data.pop("first_name", "")
        last_name = validated_data.pop("last_name", "")
        role = validated_data.pop("role", Role.PATIENT)
        profile_data = validated_data

        user = CustomUser.objects.create_user(
            email=email,
            phone_number=phone_number,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=False,
            is_superuser=False,
        )
        PublicUserProfile.objects.create(user=user, role=role)
        profile = PatientProfile(user=user, role=role, **profile_data)
        profile.save()
        return profile
