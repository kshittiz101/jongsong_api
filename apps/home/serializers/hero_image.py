from rest_framework import serializers

from ..models import HeroImage


class HeroImageSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = HeroImage
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
