from django.contrib import admin
from apps.orders.models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'store', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'store']
    search_fields = ['store__name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]
    ordering = ['-created_at']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity_requested', 'created_at']
    list_filter = ['created_at', 'order__status']
    search_fields = ['product__title', 'order__id']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
