from rest_framework import serializers
from pharmacy.models import Supplier, Category, Medicine

class SupplierSerializer(serializers.ModelSerializer):
    """
    Serializer for the Supplier model.
    """
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class MedicineSerializer(serializers.ModelSerializer):
    total_stock = serializers.IntegerField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    days_to_expiry = serializers.IntegerField(read_only=True, allow_null=True)
    is_expiring_soon = serializers.BooleanField(read_only=True)

    class Meta:
        model = Medicine
        fields = '__all__'
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'selling_price_after_discount',
        ]