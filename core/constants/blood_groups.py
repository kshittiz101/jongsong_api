from django.db import models

class BloodGroup(models.TextChoices):
    A_POSITIVE = "A+", "A Positive"
    A_NEGATIVE = "A-", "A Negative"
    B_POSITIVE = "B+", "B Positive"
    B_NEGATIVE = "B-", "B Negative"
    AB_POSITIVE = "AB+", "AB Positive"
    AB_NEGATIVE = "AB-", "AB Negative"
    O_POSITIVE = "O+", "O Positive"
    O_NEGATIVE = "O-", "O Negative"
    UNKNOWN = "UNK", "Unknown"