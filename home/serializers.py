from rest_framework import serializers

from home.models import Feature, Services


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

