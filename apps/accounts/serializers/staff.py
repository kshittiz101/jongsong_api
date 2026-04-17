from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from common.constants.roles import Role

from ..models import Designation, StaffProfile
from ._common import default_designation_instance

User = get_user_model()

# Writable staff profile fields (excludes user FK, auto timestamps, designation handled on create/update).
_STAFF_PROFILE_EXTRA_FIELDS = (
    "role",
    "profile_picture",
    "citizenship_image",
    "highest_degree",
    "address",
    "field_of_study",
    "university",
    "graduation_year",
)


class DesignationNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ["id", "name"]


class StaffProfileAdminSerializer(serializers.ModelSerializer):
    designation = DesignationNestedSerializer(read_only=True)
    role = serializers.CharField(read_only=True)

    class Meta:
        model = StaffProfile
        fields = [
            "role",
            "designation",
            "profile_picture",
            "highest_degree",
            "address",
            "citizenship_image",
            "field_of_study",
            "university",
            "graduation_year",
            "created_at",
            "updated_at",
        ]


class StaffAdminListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    staff_profile = StaffProfileAdminSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "full_name",
            "is_active",
            "is_staff",
            "date_joined",
            "last_login",
            "staff_profile",
        ]
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.get_full_name() or ""


class StaffAdminDetailSerializer(serializers.ModelSerializer):
    staff_profile = StaffProfileAdminSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
            "last_login",
            "staff_profile",
        ]
        read_only_fields = fields


class StaffAdminCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, style={"input_type": "password"})
    password2 = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        label="Confirm password",
    )
    designation = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.all(),
        required=False,
        allow_null=False,
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    phone_number = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    role = serializers.ChoiceField(
        choices=Role.choices, required=False, default=Role.PHARMACY_STAFF
    )
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    citizenship_image = serializers.ImageField(required=False, allow_null=True)
    highest_degree = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=100
    )
    address = serializers.CharField(required=False, allow_blank=True, default="")
    field_of_study = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=100
    )
    university = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    graduation_year = serializers.IntegerField(
        required=False, allow_null=True, min_value=1, max_value=9999
    )

    class Meta:
        model = User
        fields = [
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "password",
            "password2",
            "designation",
            "role",
            "profile_picture",
            "citizenship_image",
            "highest_degree",
            "address",
            "field_of_study",
            "university",
            "graduation_year",
        ]

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")

        if password != password2:
            raise serializers.ValidationError(
                {"password2": "Passwords do not match."})

        try:
            validate_password(password=password)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2", None)
        password = validated_data.pop("password")
        designation = validated_data.pop("designation", None)
        if designation is None:
            designation = default_designation_instance()

        profile_data = {}
        for key in _STAFF_PROFILE_EXTRA_FIELDS:
            if key in validated_data:
                profile_data[key] = validated_data.pop(key)
        if "role" not in profile_data:
            profile_data["role"] = Role.PHARMACY_STAFF

        user = User.objects.create_user(
            password=password,
            is_staff=True,
            is_superuser=False,
            is_active=True,
            **validated_data,
        )
        StaffProfile.objects.create(
            user=user,
            designation=designation,
            **profile_data,
        )
        return user


class StaffAdminUpdateSerializer(serializers.ModelSerializer):
    designation = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.all(),
        required=False,
        allow_null=False,
    )
    role = serializers.ChoiceField(choices=Role.choices, required=False)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    citizenship_image = serializers.ImageField(required=False, allow_null=True)
    highest_degree = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=100
    )
    address = serializers.CharField(required=False, allow_blank=True)
    field_of_study = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=100
    )
    university = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=200
    )
    graduation_year = serializers.IntegerField(
        required=False, allow_null=True, min_value=1, max_value=9999
    )

    class Meta:
        model = User
        fields = [
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "is_active",
            "designation",
            "role",
            "profile_picture",
            "citizenship_image",
            "highest_degree",
            "address",
            "field_of_study",
            "university",
            "graduation_year",
        ]
        extra_kwargs = {
            "email": {"required": False, "allow_blank": False},
            "phone_number": {"required": False, "allow_blank": False},
            "first_name": {"required": False, "allow_blank": True},
            "last_name": {"required": False, "allow_blank": True},
            "is_active": {"required": False},
        }

    def validate(self, attrs):
        incoming_keys = set(getattr(self, "initial_data", {}).keys())
        allowed_keys = set(self.fields.keys())
        forbidden_keys = {"is_staff", "is_superuser", "admin_profile"}

        unknown_keys = incoming_keys - allowed_keys
        if unknown_keys:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        f"Unknown field(s): {', '.join(sorted(unknown_keys))}."
                    ]
                }
            )

        bad_keys = incoming_keys & forbidden_keys
        if bad_keys:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        f"Forbidden field(s): {', '.join(sorted(bad_keys))}."
                    ]
                }
            )

        email = attrs.get("email")
        if email:
            qs = User.objects.filter(
                email__iexact=email).exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"email": ["This email is already in use."]})

        phone = attrs.get("phone_number")
        if phone:
            qs = User.objects.filter(phone_number__iexact=phone).exclude(
                pk=self.instance.pk
            )
            if qs.exists():
                raise serializers.ValidationError(
                    {"phone_number": ["This phone number is already in use."]}
                )

        return attrs

    def update(self, instance, validated_data):
        designation = validated_data.pop("designation", None)

        profile_updates = {}
        for key in _STAFF_PROFILE_EXTRA_FIELDS:
            if key in validated_data:
                profile_updates[key] = validated_data.pop(key)

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        staff_profile = getattr(instance, "staff_profile", None)
        if staff_profile:
            if designation is not None:
                staff_profile.designation = designation
            for field_name, value in profile_updates.items():
                setattr(staff_profile, field_name, value)
            staff_profile.save()

        return instance
