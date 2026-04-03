from rest_framework import serializers

from ..models import Feature


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
