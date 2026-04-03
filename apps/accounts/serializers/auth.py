from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from common.constants.roles import Role

from ..models import AdminProfile, CustomUser, Designation, PublicUserProfile, StaffProfile
from ._common import default_designation_instance


class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ["id", "name", "description"]
        read_only_fields = ["id"]
        extra_kwargs = {
            "name": {
                "validators": [UniqueValidator(queryset=Designation.objects.all())],
            },
        }


DesignationReadSerializer = DesignationSerializer


class AdminCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
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
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    phone_number = serializers.CharField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "phone_number",
            "password",
            "password2",
            "designation",
            "profile_picture",
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
        designation = validated_data.pop("designation", None)
        if designation is None:
            designation = default_designation_instance()
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
    designation = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.all(),
        required=False,
        allow_null=False,
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    phone_number = serializers.CharField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )

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
        designation = validated_data.pop("designation", None)
        if designation is None:
            designation = default_designation_instance()

        user = CustomUser.objects.create_user(
            password=password,
            is_staff=True,
            is_superuser=False,
            **validated_data,
        )
        StaffProfile.objects.create(
            user=user,
            role=Role.STAFF,
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
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    phone_number = serializers.CharField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password",
            "password2",
        ]
        read_only_fields = ["id"]

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


def serialize_auth_user(user, request=None):
    """
    Shape matches the frontend `UserProfile` type (role/avatar from linked profile).
    """
    admin = getattr(user, "admin_profile", None)
    staff = getattr(user, "staff_profile", None)
    public = getattr(user, "publicuserprofile", None)

    role = Role.CUSTOMER
    avatar_url = ""

    if admin:
        role = admin.role
        if admin.profile_picture:
            avatar_url = admin.profile_picture.url
    elif staff:
        role = staff.role
        if staff.profile_picture:
            avatar_url = staff.profile_picture.url
    elif public:
        role = public.role
    elif user.is_superuser:
        role = Role.ADMIN

    if request and avatar_url and not str(avatar_url).startswith("http"):
        avatar_url = request.build_absolute_uri(avatar_url)

    display_name = user.get_full_name() or user.email or user.username

    return {
        "id": user.id,
        "username": user.username,
        "phone": user.phone_number,
        "email": user.email,
        "full_name": user.get_full_name() or "",
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "date_joined": user.date_joined.isoformat() if user.date_joined else "",
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "profile": {
            "role": role,
            "display_name": display_name,
            "avatar_url": avatar_url or "",
        },
    }


class LoginTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Production login: accepts a single identifier (email/phone/username) + password,
    returns access/refresh tokens only.
    """

    identifier = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop(get_user_model().USERNAME_FIELD, None)

    default_error_messages = {
        "not_registered": "User is not registered.",
        "password_not_matched": "Password is not matched.",
        "inactive": "User account is inactive.",
    }

    def validate(self, attrs):
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
            raise serializers.ValidationError(
                {"identifier": [self.error_messages["not_registered"]]}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"identifier": [self.error_messages["inactive"]]}
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                {"password": [self.error_messages["password_not_matched"]]}
            )

        refresh = self.get_token(user)

        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["uid"] = user.id
        token["email"] = user.email
        token["phone_number"] = user.phone_number
        token["is_staff"] = user.is_staff
        token["is_superuser"] = user.is_superuser
        return token
