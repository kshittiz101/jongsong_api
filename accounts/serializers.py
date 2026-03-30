from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.constants.designations import Designations
from core.constants.roles import Role
from normal_user.models import PublicUserProfile
from staff.models import StaffProfile

from .models import AdminProfile, CustomUser


class AdminCreateSerializer(serializers.ModelSerializer):
    
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
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    email = serializers.EmailField(validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    phone_number = serializers.CharField(validators=[UniqueValidator(queryset=CustomUser.objects.all())])

    class Meta:
        model = CustomUser
        fields = ["email", "phone_number", "password", "password2", "designation", "profile_picture"]

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
        profile_picture = validated_data.pop("profile_picture", None)

        user = CustomUser.objects.create_user(
            password=password,
            is_staff=True,
            is_superuser=False,
            **validated_data,
        )
        AdminProfile.objects.create(
            user=user,
            role=Role.ADMIN,
            designation=designation,
            profile_picture=profile_picture,
        )
        return user


class StaffCreateSerializer(serializers.ModelSerializer):
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
    email = serializers.EmailField(validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    phone_number = serializers.CharField(validators=[UniqueValidator(queryset=CustomUser.objects.all())])

    class Meta:
        model = CustomUser
        fields = ["email", "phone_number", "password", "password2", "designation"]

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

        user = CustomUser.objects.create_user(
            password=password,
            is_staff=True,
            is_superuser=False,
            **validated_data,
        )
        StaffProfile.objects.create(
            user=user,
            role=Role.OTHER,
            designation=designation,
        )
        return user


class PublicUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password2 = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        label="Confirm password",
    )
    email = serializers.EmailField(validators=[UniqueValidator(queryset=CustomUser.objects.all())])
    phone_number = serializers.CharField(validators=[UniqueValidator(queryset=CustomUser.objects.all())])

    class Meta:
        model = CustomUser
        fields = ["email", "phone_number", "password", "password2"]

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

        user = CustomUser.objects.create_user(
            password=password,
            is_staff=False,
            is_superuser=False,
            **validated_data,
        )
        PublicUserProfile.objects.create(user=user, role=Role.CUSTOMER)
        return user


class LoginTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Production login: accepts a single identifier (email/phone/username) + password,
    returns access/refresh plus a small user payload.
    """

    identifier = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # SimpleJWT adds USERNAME_FIELD (email here); we authenticate via identifier only.
        self.fields.pop(get_user_model().USERNAME_FIELD, None)

    default_error_messages = {
        "not_registered": "User is not registered.",
        "password_not_matched": "Password is not matched.",
        "inactive": "User account is inactive.",
    }

    def validate(self, attrs):
        request = self.context.get("request")
        identifier = (attrs.get("identifier") or "").strip()
        password = attrs.get("password")

        if not identifier:
            raise serializers.ValidationError(
                {"identifier": ["This field may not be blank."]}
            )

        UserModel = get_user_model()
        try:
            user = UserModel._default_manager.get(
                Q(username__iexact=identifier)
                | Q(email__iexact=identifier)
                | Q(phone_number__iexact=identifier)
            )
        except UserModel.DoesNotExist:
            raise serializers.ValidationError({"identifier": [self.error_messages["not_registered"]]})

        if not user.is_active:
            raise serializers.ValidationError({"identifier": [self.error_messages["inactive"]]})

        if not user.check_password(password):
            raise serializers.ValidationError({"password": [self.error_messages["password_not_matched"]]})

        refresh = self.get_token(user)

        # Minimal, stable response surface for clients
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
          
        }
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Helpful claims for downstream services/UI; keep non-sensitive.
        token["uid"] = user.id
        token["email"] = user.email
        token["phone_number"] = user.phone_number
        token["is_staff"] = user.is_staff
        token["is_superuser"] = user.is_superuser
        return token
