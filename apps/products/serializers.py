from rest_framework import serializers
from apps.products.models import Category, Product, Store, Inventory

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category', 'category_name', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'location', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class InventorySerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    category_name = serializers.CharField(source='product.category.name', read_only=True)

    class Meta:
        model = Inventory
        fields = ['id', 'store', 'product', 'product_title', 'product_price', 'category_name', 'quantity', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
