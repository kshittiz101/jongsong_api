from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from core.constants.designations import Designations
from core.constants.roles import Role
from staff.models import StaffProfile


User = get_user_model()


class StaffProfileAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProfile
        fields = [
            "designation",
            "highest_degree",
            "address",
            "field_of_study",
            "university",
            "graduation_year",
        ]


class StaffAdminListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    designation = serializers.CharField(source="staff_profile.designation", read_only=True)

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
            "date_joined",
            "designation",
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
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password2 = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        label="Confirm password",
    )
    designation = serializers.ChoiceField(
        choices=Designations.choices,
        required=False,
        default=Designations.OTHER,
    )
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    phone_number = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all())])

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
        ]

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")

        if password != password2:
            raise serializers.ValidationError({"password2": "Passwords do not match."})

        try:
            validate_password(password=password)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2", None)
        password = validated_data.pop("password")
        designation = validated_data.pop("designation", Designations.OTHER)

        user = User.objects.create_user(
            password=password,
            is_staff=True,
            is_superuser=False,
            is_active=True,
            **validated_data,
        )
        StaffProfile.objects.create(
            user=user,
            role=Role.STAFF,
            designation=designation,
        )
        return user


class StaffAdminUpdateSerializer(serializers.ModelSerializer):
    designation = serializers.ChoiceField(
        choices=Designations.choices,
        required=False,
    )

    class Meta:
        model = User
        fields = ["email", "phone_number", "first_name", "last_name", "is_active", "designation"]
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
        forbidden_keys = {"is_staff", "is_superuser", "role", "admin_profile"}

        unknown_keys = incoming_keys - allowed_keys
        if unknown_keys:
            raise serializers.ValidationError(
                {"non_field_errors": [f"Unknown field(s): {', '.join(sorted(unknown_keys))}."]}
            )

        bad_keys = incoming_keys & forbidden_keys
        if bad_keys:
            raise serializers.ValidationError(
                {"non_field_errors": [f"Forbidden field(s): {', '.join(sorted(bad_keys))}."]}
            )

        email = attrs.get("email")
        if email:
            qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"email": ["This email is already in use."]})

        phone = attrs.get("phone_number")
        if phone:
            qs = User.objects.filter(phone_number__iexact=phone).exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"phone_number": ["This phone number is already in use."]})

        return attrs

    def update(self, instance, validated_data):
        designation = validated_data.pop("designation", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        staff_profile = getattr(instance, "staff_profile", None)
        if staff_profile:
            staff_profile.role = Role.STAFF
            if designation is not None:
                staff_profile.designation = designation
            staff_profile.save()

        return instance
