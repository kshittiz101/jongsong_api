from rest_framework import serializers

from ..models import Services


class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
