from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.accounts.models import PatientProfile
from apps.accounts.serializers import PatientProfileSerializer
from common.constants.patient_types import PatientType
from common.permissions import IsAdminOrSuperUser

from ..serializers.patient_management import (
    HomeCarePatientCreateSerializer,
    HomeCarePatientUpdateSerializer,
)

_TAG = ["home care patients"]


@extend_schema_view(
    list=extend_schema(tags=_TAG),
    retrieve=extend_schema(tags=_TAG),
    create=extend_schema(tags=_TAG),
)
class HomeCarePatientViewSet(viewsets.ModelViewSet):
    """
    Admin-only portal API for home-care patients (backed by `accounts.PatientProfile`).

    Detail URLs use the **patient user id** (`PatientProfile.user_id`).
    """

    permission_classes = [IsAdminOrSuperUser]
    lookup_field = "user_id"
    lookup_url_kwarg = "pk"
    http_method_names = ["get", "post", "patch", "head", "options"]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "user__email",
        "user__phone_number",
        "user__first_name",
        "user__last_name",
        "unique_health_id",
    ]
    ordering_fields = ("created_at", "admission_date", "discharge_date", "unique_health_id")
    ordering = ("-created_at",)

    def get_queryset(self):
        return PatientProfile.objects.select_related("user").filter(
            patient_type=PatientType.HOME_CARE
        )

    def _apply_list_filters(self, qs):
        params = self.request.query_params
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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self._apply_list_filters(self.get_queryset()))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PatientProfileSerializer(
                page, many=True, context=self.get_serializer_context()
            )
            return self.get_paginated_response(serializer.data)
        serializer = PatientProfileSerializer(
            queryset, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == "create":
            return HomeCarePatientCreateSerializer
        if self.action == "partial_update":
            return HomeCarePatientUpdateSerializer
        return PatientProfileSerializer

    def create(self, request, *args, **kwargs):
        serializer = HomeCarePatientCreateSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        output = PatientProfileSerializer(profile, context=self.get_serializer_context())
        headers = self.get_success_headers(output.data)
        return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)

    def partial_update(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = HomeCarePatientUpdateSerializer(
            data=request.data,
            partial=True,
            context={**self.get_serializer_context(), "user": profile.user, "profile": profile},
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(profile, serializer.validated_data)
        profile.refresh_from_db()
        profile.user.refresh_from_db()
        return Response(
            PatientProfileSerializer(profile, context=self.get_serializer_context()).data
        )
