from django.db.models.deletion import ProtectedError
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    AdminCreateSerializer,
    DesignationSerializer,
    PublicUserCreateSerializer,
    StaffCreateSerializer,
    LoginTokenObtainPairSerializer,
    serialize_auth_user,
)
from .models import CustomUser, Designation
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

from core.parsers import PlainTextJSONParser
from core.permissions import IsAdminOrSuperUser, IsSuperUser

_AUTH_PARSER_CLASSES = [JSONParser, PlainTextJSONParser]

_AUTH_OPENAPI_TAG = ["auth"]
_ADMIN_OPENAPI_TAG = ["admin"]



@extend_schema(tags=_AUTH_OPENAPI_TAG)
class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = LoginTokenObtainPairSerializer
    parser_classes = _AUTH_PARSER_CLASSES


@extend_schema(tags=_AUTH_OPENAPI_TAG)
class CurrentUserView(APIView):
    """GET current user — same shape as the `user` object on login."""

    permission_classes = [IsAuthenticated]
    parser_classes = _AUTH_PARSER_CLASSES

    def get(self, request):
        return Response(serialize_auth_user(request.user, request))


@extend_schema(tags=_AUTH_OPENAPI_TAG)
class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    parser_classes = _AUTH_PARSER_CLASSES


@extend_schema(tags=_AUTH_OPENAPI_TAG)
class LogoutView(APIView):
    """
    Logout by blacklisting the provided refresh token.
    Clients should call this on sign-out.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = _AUTH_PARSER_CLASSES

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"refresh": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except Exception:
            return Response(
                {"refresh": ["Invalid token."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)



@extend_schema(tags=_AUTH_OPENAPI_TAG)
class AdminRegistrationBySuperuserView(generics.CreateAPIView):
    """Register a new admin user by a superuser."""
    queryset = CustomUser.objects.all()
    serializer_class = AdminCreateSerializer
    permission_classes = [IsSuperUser]
    parser_classes = [JSONParser, FormParser, MultiPartParser]


@extend_schema(tags=_AUTH_OPENAPI_TAG)
class StaffRegistrationBySuperuserView(generics.CreateAPIView):
    """Register a new staff user by a superuser."""
    queryset = CustomUser.objects.all()
    serializer_class = StaffCreateSerializer
    permission_classes = [IsSuperUser]
    parser_classes = [JSONParser]




@extend_schema(tags=_AUTH_OPENAPI_TAG)
class PublicUserRegistrationView(generics.CreateAPIView):
    """Register a new public user."""
    queryset = CustomUser.objects.all()
    serializer_class = PublicUserCreateSerializer
    permission_classes = [IsSuperUser]
    parser_classes = [JSONParser, FormParser, MultiPartParser]




@extend_schema(tags=_ADMIN_OPENAPI_TAG)
class DesignationListCreateView(generics.ListCreateAPIView):
    """List and create designations (admin UI and management)."""

    permission_classes = [IsAdminOrSuperUser]
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer
    parser_classes = _AUTH_PARSER_CLASSES


@extend_schema(tags=_ADMIN_OPENAPI_TAG)
class DesignationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a single designation."""

    permission_classes = [IsAdminOrSuperUser]
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer
    parser_classes = _AUTH_PARSER_CLASSES

    def perform_destroy(self, instance):
        if instance.name == "Other":
            raise ValidationError(
                {"detail": 'Cannot delete the reserved "Other" designation.'}
            )
        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError(
                {"detail": "Cannot delete a designation that is assigned to users."}
            )
