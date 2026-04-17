from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

from common.constants.roles import Role
from common.permissions import IsAdminOrSuperUser, IsDashboardStaffOrAdmin

from ..serializers.auth import DashboardUserUpdateSerializer, serialize_auth_user

User = get_user_model()


def _user_list_queryset(role_param: str | None):
    qs = (
        User.objects.all()
        .select_related(
            "admin_profile",
            "staff_profile__designation",
            "publicuserprofile",
            "patient_profile",
        )
        .order_by("-date_joined", "id")
    )
    if not role_param or not str(role_param).strip():
        return qs
    r = str(role_param).strip().upper()
    if r == "ADMIN":
        return qs.filter(admin_profile__isnull=False)
    if r in ("STAFF", "HOMECARE"):
        return qs.filter(staff_profile__isnull=False)
    if r in ("PUBLIC", "CUSTOMER"):
        return qs.filter(publicuserprofile__role=Role.CUSTOMER)
    if r == "PATIENT":
        return qs.filter(
            publicuserprofile__role__in=[Role.PATIENT, Role.HOME_CARE_PATIENT]
        )
    return qs


class UserListView(APIView):
    """GET /api/v1/users/?role= — plain list for jongsong-ui (no pagination)."""

    permission_classes = [IsDashboardStaffOrAdmin]

    def get(self, request):
        qs = _user_list_queryset(request.query_params.get("role"))
        data = [serialize_auth_user(u, request) for u in qs]
        return Response(data)


class UserDetailView(APIView):
    """GET|PATCH|DELETE /api/v1/users/<id>/"""

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsDashboardStaffOrAdmin()]
        return [IsAdminOrSuperUser()]

    def get(self, request, pk):
        user = get_object_or_404(
            User.objects.select_related(
                "admin_profile",
                "staff_profile__designation",
                "publicuserprofile",
                "patient_profile",
            ),
            pk=pk,
        )
        return Response(serialize_auth_user(user, request))

    def patch(self, request, pk):
        user = get_object_or_404(User.objects.select_related(), pk=pk)
        ser = DashboardUserUpdateSerializer(user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        user.refresh_from_db()
        return Response(serialize_auth_user(user, request))

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if not user.is_superuser:
            user.is_active = False
            user.save(update_fields=["is_active"])
        return Response(status=204)
