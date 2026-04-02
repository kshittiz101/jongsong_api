from django.db import models

class PatientType(models.TextChoices):
    HOME_CARE = "home_care", "Home Care"
    PHARMACY = "pharmacy", "Pharmacy"
    OTHER = "other", "Other"