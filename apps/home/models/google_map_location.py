from django.db import models


class Location(models.Model):
    '''
    Model to store location information with Google Maps embed code
    '''
    name = models.CharField(
        max_length=200, help_text="Location name ")
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    google_location_links = models.TextField(
        help_text="Store Google Maps share links")
    google_maps_embed = models.TextField(
        help_text="Paste the Google Maps iframe embed code here"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def full_address(self):
        """Return the complete formatted address"""
        return f"{self.street}, {self.city}, {self.postal_code}"
