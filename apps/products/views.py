from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from apps.products.models import Category, Product, Store, Inventory
from apps.products.serializers import CategorySerializer, ProductSerializer, StoreSerializer, InventorySerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['category']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'title']
    ordering = ['-created_at']


class StoreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    pagination_class = StandardResultsSetPagination


class InventoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InventorySerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        store_id = self.kwargs.get('store_id')
        return Inventory.objects.filter(store_id=store_id).select_related('product', 'product__category')

    def list(self, request, *args, **kwargs):
        store_id = kwargs.get('store_id')
        cache_key = f'inventory_store_{store_id}'

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset().order_by('product__title')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            cache.set(cache_key, serializer.data, 300)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, 300)
        return Response(serializer.data)
