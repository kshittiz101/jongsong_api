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
    total_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    days_to_expiry = serializers.ReadOnlyField()
    is_expiring_soon = serializers.ReadOnlyField()

    class Meta:
        model = Medicine
        fields = '__all__'
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'selling_price_after_discount',
        ]