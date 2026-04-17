from django.db import models


class Role(models.TextChoices):
    ADMIN = "admin", "Admin"
    CUSTOMER = "customer", "Customer"

    # staff
    STAFF = "staff", "Staff"
    # home care staff
    HOME_CARE_STAFF = "home_care_staff", "Home Care Staff"

    # pharmacy staff
    PHARMACY_STAFF = "pharmacy_staff", "Pharmacy Staff"

    # home care patient
    HOME_CARE_PATIENT = "home_care_patient", "Home Care Patient"
    PATIENT = "patient", "Patient"
