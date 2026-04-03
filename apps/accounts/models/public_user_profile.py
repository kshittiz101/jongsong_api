from django.db import models

from common.constants.roles import Role

from .user import CustomUser


class PublicUserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=100, choices=Role.choices, default=Role.CUSTOMER
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Public User Profile of {self.user.username}"
