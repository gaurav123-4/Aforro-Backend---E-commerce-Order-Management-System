from rest_framework import serializers
from apps.orders.models import Order, OrderItem
from apps.products.serializers import ProductSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_details', 'quantity_requested', 'created_at']
        read_only_fields = ['created_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'store', 'store_name', 'status', 'items', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'status']


class OrderCreateSerializer(serializers.Serializer):
    store_id = serializers.IntegerField()
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        )
    )

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required")
        for item in value:
            if 'product_id' not in item or 'quantity_requested' not in item:
                raise serializers.ValidationError(
                    "Each item must have 'product_id' and 'quantity_requested'"
                )
            if item['quantity_requested'] <= 0:
                raise serializers.ValidationError(
                    "Quantity must be greater than 0"
                )
        return value
