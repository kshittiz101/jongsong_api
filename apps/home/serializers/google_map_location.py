from rest_framework import serializers
from ..models import Location


class LocationSerializer(serializers.ModelSerializer):
    full_address = serializers.ReadOnlyField()

    class Meta:
        model = Location
        fields = [
            'id', 'name', 'street', 'city', 'postal_code',
            'full_address', 'google_location_links', 'google_maps_embed',
            'created_at'
        ]
