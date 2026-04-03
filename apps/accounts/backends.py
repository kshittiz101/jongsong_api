from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrPhoneBackend(ModelBackend):
    """
    Authenticate using a single identifier that can be:
    - username
    - email
    - phone_number
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        identifier = (
            kwargs.get("identifier")
            or kwargs.get(UserModel.USERNAME_FIELD)
            or username
        )
        if not identifier or password is None:
            return None

        identifier = str(identifier).strip()

        try:
            user = UserModel._default_manager.get(
                Q(username__iexact=identifier)
                | Q(email__iexact=identifier)
                | Q(phone_number__iexact=identifier)
            )
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

