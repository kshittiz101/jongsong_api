from django.db import models


class Role(models.TextChoices):
    ADMIN = "admin", "Admin"
    STAFF = "staff", "Staff"
    DOCTOR = "doctor", "Doctor"
    NURSE = "nurse", "Nurse"
    CUSTOMER = "customer", "Customer"
    PATIENT = "patient", "Patient"
    HOMECARE_PATIENT = "homecare_patient", "Homecare Patient"
    PHARMACY_STAFF = "pharmacy_staff", "Pharmacy Staff"
    LAB_TECHNICIAN = "lab_technician", "Lab Technician"
    HOMECARE_STAFF = "homecare_staff", "Homecare Staff"
    OTHER = "other", "Other"


