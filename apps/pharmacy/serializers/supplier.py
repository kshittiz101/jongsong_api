from rest_framework import serializers

from ..models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    """
    Serializer for the Supplier model.
    """

    class Meta:
        model = Supplier
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
