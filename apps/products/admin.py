from django.contrib import admin
from apps.products.models import Category, Product, Store, Inventory

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['-created_at']


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'created_at']
    search_fields = ['name', 'location']
    ordering = ['name']


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['store', 'product', 'quantity', 'updated_at']
    list_filter = ['store', 'updated_at']
    search_fields = ['product__title', 'store__name']
    ordering = ['store', 'product']
