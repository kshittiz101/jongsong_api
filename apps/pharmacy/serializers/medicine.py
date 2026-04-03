from rest_framework import serializers

from ..models import Medicine


class MedicineSerializer(serializers.ModelSerializer):
    total_stock = serializers.IntegerField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    days_to_expiry = serializers.IntegerField(read_only=True, allow_null=True)
    is_expiring_soon = serializers.BooleanField(read_only=True)

    class Meta:
        model = Medicine
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "selling_price_after_discount",
        ]
