from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    AdminCreateSerializer,
    PublicUserCreateSerializer,
    StaffCreateSerializer,
    LoginTokenObtainPairSerializer,
)
from .models import CustomUser
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser

from core.parsers import PlainTextJSONParser
from core.permissions import IsSuperUser

_AUTH_PARSER_CLASSES = [JSONParser, PlainTextJSONParser]

class AdminRegistrationBySuperuserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AdminCreateSerializer
    permission_classes = [IsSuperUser]
    parser_classes = [JSONParser, FormParser, MultiPartParser]


class StaffRegistrationBySuperuserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = StaffCreateSerializer
    permission_classes = [IsSuperUser]
    parser_classes = [JSONParser]


class PublicUserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = PublicUserCreateSerializer
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = LoginTokenObtainPairSerializer
    parser_classes = _AUTH_PARSER_CLASSES


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    parser_classes = _AUTH_PARSER_CLASSES


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