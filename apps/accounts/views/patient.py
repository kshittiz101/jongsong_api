from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from common.permissions import IsAdminOrSuperUser

from ..models import PatientProfile
from ..permissions import PatientProfilePermission
from ..serializers import (
    PatientProfileAdminCreateSerializer,
    PatientProfileSerializer,
    PatientUserOnboardingSerializer,
)

_PATIENT_TAG = ["patient profiles"]


@extend_schema(tags=_PATIENT_TAG)
class PatientUserOnboardingView(CreateAPIView):
    """
    Create login user, PublicUserProfile (role patient), and PatientProfile.

    Admin (or superuser) only.
    """

    permission_classes = [IsAdminOrSuperUser]
    serializer_class = PatientUserOnboardingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        output = PatientProfileSerializer(
            profile,
            context={"request": request},
        )
        return Response(output.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(tags=_PATIENT_TAG),
    retrieve=extend_schema(tags=_PATIENT_TAG),
    create=extend_schema(tags=_PATIENT_TAG),
    update=extend_schema(tags=_PATIENT_TAG),
    partial_update=extend_schema(tags=_PATIENT_TAG),
)
class PatientProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [PatientProfilePermission]
    queryset = PatientProfile.objects.select_related("user").all()
    http_method_names = ["get", "post", "put", "patch", "head", "options"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser or hasattr(user, "admin_profile"):
            return qs
        return qs.filter(user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return PatientProfileAdminCreateSerializer
        return PatientProfileSerializer

    @extend_schema(
        tags=_PATIENT_TAG,
        responses={200: PatientProfileSerializer},
    )
    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request, *args, **kwargs):
        profile = get_object_or_404(
            PatientProfile.objects.select_related("user"), user=request.user
        )
        if request.method == "GET":
            serializer = PatientProfileSerializer(
                profile,
                context={"request": request},
            )
            return Response(serializer.data)
        serializer = PatientProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
