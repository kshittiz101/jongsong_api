from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.constants.patient_types import PatientType
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
    destroy=extend_schema(tags=_PATIENT_TAG),
)
class PatientProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [PatientProfilePermission]
    queryset = PatientProfile.objects.select_related("user").all()
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "user__email",
        "user__phone_number",
        "user__first_name",
        "user__last_name",
        "unique_health_id",
    ]
    ordering_fields = [
        "created_at",
        "admission_date",
        "discharge_date",
        "unique_health_id",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = PatientProfile.objects.select_related("user")
        user = self.request.user
        is_admin = user.is_superuser or hasattr(user, "admin_profile")
        if not is_admin:
            return qs.filter(user=user)
        if self.action == "list":
            qs = self._apply_admin_list_filters(qs)
        return qs

    def _apply_admin_list_filters(self, qs):
        """Exact-match filters for admin list only (no django-filter dependency)."""
        params = self.request.query_params
        patient_type_raw = params.get("patient_type")
        if patient_type_raw is not None and patient_type_raw.strip() != "":
            pt = patient_type_raw.strip()
            collapsed = pt.lower().replace("_", "").replace("-", "")
            if collapsed == "homecare":
                pt = PatientType.HOME_CARE
            qs = qs.filter(patient_type=pt)
        for field in ("gender", "blood_group"):
            val = params.get(field)
            if val is not None and val != "":
                qs = qs.filter(**{field: val})
        phone = params.get("phone_number")
        if phone is not None and phone.strip() != "":
            qs = qs.filter(user__phone_number=phone.strip())
        if "is_active_patient" in params:
            raw = (params.get("is_active_patient") or "").lower()
            if raw in ("true", "1", "yes"):
                qs = qs.filter(is_active_patient=True)
            elif raw in ("false", "0", "no"):
                qs = qs.filter(is_active_patient=False)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return PatientProfileAdminCreateSerializer
        return PatientProfileSerializer

    def create(self, request, *args, **kwargs):
        serializer = PatientProfileAdminCreateSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        output = PatientProfileSerializer(
            profile,
            context={"request": request},
        )
        headers = self.get_success_headers(output.data)
        return Response(
            output.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


@extend_schema(tags=_PATIENT_TAG)
class PatientProfileMeView(APIView):
    """
    Current user's patient profile (not under /admin/).

    Any authenticated user may call this; returns 404 if they have no PatientProfile.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: PatientProfileSerializer})
    def get(self, request, *args, **kwargs):
        profile = get_object_or_404(
            PatientProfile.objects.select_related("user"),
            user=request.user,
        )
        serializer = PatientProfileSerializer(
            profile,
            context={"request": request},
        )
        return Response(serializer.data)

    @extend_schema(
        request=PatientProfileSerializer,
        responses={200: PatientProfileSerializer},
    )
    def patch(self, request, *args, **kwargs):
        profile = get_object_or_404(
            PatientProfile.objects.select_related("user"),
            user=request.user,
        )
        serializer = PatientProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
