from django.db import models


class Role(models.TextChoices):
    ADMIN = "admin", "Admin"
    CUSTOMER = "customer", "Customer"
    STAFF = "staff", "Staff"
    PATIENT = "patient", "Patient"
