from django.core import validators
from django.db import models
from django.utils.timezone import now


class Prescription(models.Model):

    '''
    This model is responsible for storing prescription information about patients.
    '''
    prescription_img = models.ImageField(
        upload_to='prescriptions/',
        validators=[validators.FileExtensionValidator(
            allowed_extensions=['png', 'jpg', 'jpeg'])]
    )
    full_name = models.CharField(
        max_length=100, db_index=True
    )
    phone_number = models.CharField(max_length=15)
    prescription_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(
        default=now, editable=False
    )
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ],
        default='pending'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Prescription for {self.full_name} - {self.created_at.date()}"
