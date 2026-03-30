from django.db import models

class Designations(models.TextChoices):
    DOCTOR = "doctor", "Doctor"
    NURSE = "nurse", "Nurse"
    LAB_TECHNICIAN = "lab_technician", "Lab Technician"
    HOMECARE_STAFF = "homecare_staff", "Homecare Staff"
    PHARMACY_STAFF = "pharmacy_staff", "Pharmacy Staff"
    OTHER = "other", "Other"