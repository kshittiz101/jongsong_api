from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from core.permissions import IsAdminOrSuperUser
from staff.serializers import (
    StaffAdminCreateSerializer,
    StaffAdminDetailSerializer,
    StaffAdminListSerializer,
    StaffAdminUpdateSerializer,
)

User = get_user_model()


class StaffManagementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrSuperUser]
    queryset = User.objects.filter(staff_profile__isnull=False)

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["email", "phone_number", "first_name", "last_name"]
    ordering_fields = ["date_joined", "email", "phone_number"]
    ordering = ["-date_joined"]

    def get_queryset(self):
        qs = super().get_queryset().select_related("staff_profile__designation")
        is_active = self.request.query_params.get("is_active")
        if is_active is None:
            return qs

        value = str(is_active).strip().lower()
        if value in {"true", "1", "yes"}:
            return qs.filter(is_active=True)
        if value in {"false", "0", "no"}:
            return qs.filter(is_active=False)
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
