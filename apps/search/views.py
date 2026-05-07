from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.core.cache import cache
from apps.products.models import Product, Category
from apps.search.serializers import ProductSearchSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class SearchViewSet(viewsets.ViewSet):
    pagination_class = StandardResultsSetPagination

    @action(detail=False, methods=['get'], url_path='products')
    def search_products(self, request):
        query = request.query_params.get('q', '').strip()
        category = request.query_params.get('category')
        price_min = request.query_params.get('price_min')
        price_max = request.query_params.get('price_max')
        store_id = request.query_params.get('store_id')
        in_stock = request.query_params.get('in_stock', 'false').lower() == 'true'
        sort_by = request.query_params.get('sort_by', 'relevance')

        cache_key = f"search_{query}_{category}_{price_min}_{price_max}_{store_id}_{in_stock}_{sort_by}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        queryset = Product.objects.select_related('category')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )

        if category:
            try:
                cat = Category.objects.get(id=category)
                queryset = queryset.filter(category=cat)
            except Category.DoesNotExist:
                pass

        if price_min:
            try:
                queryset = queryset.filter(price__gte=float(price_min))
            except (ValueError, TypeError):
                pass

        if price_max:
            try:
                queryset = queryset.filter(price__lte=float(price_max))
            except (ValueError, TypeError):
                pass

        if store_id and in_stock:
            queryset = queryset.filter(
                inventory__store_id=store_id,
                inventory__quantity__gt=0
            ).distinct()

        if sort_by == 'price':
            queryset = queryset.order_by('price')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('-created_at')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = ProductSearchSerializer(page, many=True)
            response_data = paginator.get_paginated_response(serializer.data)
            cache.set(cache_key, response_data.data, 300)
            return response_data

        serializer = ProductSearchSerializer(queryset, many=True)
        cache.set(cache_key, {'results': serializer.data}, 300)
        return Response({'results': serializer.data})

    @action(detail=False, methods=['get'], url_path='suggest')
    def autocomplete(self, request):
        query = request.query_params.get('q', '').strip()

        if not query or len(query) < 2:
            return Response({'suggestions': []})

        cache_key = f"autocomplete_{query}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        products = Product.objects.filter(
            Q(title__istartswith=query) |
            Q(category__name__istartswith=query)
        ).values('title', 'category__name').distinct()[:10]

        suggestions = list(set([p['title'] for p in products] + [p['category__name'] for p in products]))

        response_data = {'suggestions': suggestions}
        cache.set(cache_key, response_data, 300)
        return Response(response_data)
