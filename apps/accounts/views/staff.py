from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from common.constants.roles import Role
from common.permissions import IsAdminOrSuperUser
from drf_spectacular.utils import extend_schema

from ..serializers import (
    StaffAdminCreateSerializer,
    StaffAdminDetailSerializer,
    StaffAdminListSerializer,
    StaffAdminUpdateSerializer,
)

User = get_user_model()


@extend_schema(tags=['Staff Management'])
class StaffManagementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrSuperUser]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    queryset = User.objects.filter(staff_profile__isnull=False)

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["email", "phone_number", "first_name", "last_name"]
    ordering_fields = ["date_joined", "email", "phone_number"]
    ordering = ["-date_joined"]

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("staff_profile__designation")
            .prefetch_related("staff_profile")
        )
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            value = str(is_active).strip().lower()
            if value in {"true", "1", "yes"}:
                qs = qs.filter(is_active=True)
            elif value in {"false", "0", "no"}:
                qs = qs.filter(is_active=False)

        role = self.request.query_params.get("role")
        if role is not None:
            role_key = str(role).strip()
            allowed = {choice.value for choice in Role}
            if role_key not in allowed:
                return qs.none()
            qs = qs.filter(staff_profile__role=role_key)

        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return StaffAdminListSerializer
        if self.action == "retrieve":
            return StaffAdminDetailSerializer
        if self.action == "create":
            return StaffAdminCreateSerializer
        if self.action in {"update", "partial_update"}:
            return StaffAdminUpdateSerializer
        return StaffAdminDetailSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_active:
            instance.is_active = False
            instance.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)
