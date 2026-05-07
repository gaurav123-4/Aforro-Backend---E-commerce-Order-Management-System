from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.cache import cache
import logging
from apps.orders.models import Order, OrderItem
from apps.orders.serializers import OrderSerializer, OrderCreateSerializer
from apps.products.models import Store, Product, Inventory
from .tasks import process_order_async

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class OrderViewSet(viewsets.ViewSet):
    pagination_class = StandardResultsSetPagination

    @action(detail=False, methods=['post'])
    def create_order(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        store_id = serializer.validated_data['store_id']
        items_data = serializer.validated_data['items']

        store = get_object_or_404(Store, id=store_id)

        try:
            with transaction.atomic():
                order = Order.objects.create(store=store, status='PENDING')

                for item_data in items_data:
                    product = get_object_or_404(Product, id=item_data['product_id'])
                    quantity = item_data['quantity_requested']

                    inventory = get_object_or_404(Inventory, store=store, product=product)

                    if inventory.quantity < quantity:
                        raise ValueError(
                            f"Insufficient stock for {product.title}. "
                            f"Available: {inventory.quantity}, Requested: {quantity}"
                        )

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity_requested=quantity
                    )

                order.status = 'CONFIRMED'
                order.save()

                with transaction.atomic():
                    for item in order.items.all():
                        inventory = Inventory.objects.select_for_update().get(
                            store=store,
                            product=item.product
                        )
                        inventory.quantity -= item.quantity_requested
                        inventory.save()

                cache.delete(f'inventory_store_{store_id}')

                try:
                    process_order_async.delay(order.id)
                except Exception as e:
                    logger.error(f'Failed to queue async task: {str(e)}')

                response_serializer = OrderSerializer(order)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            order.status = 'REJECTED'
            order.save()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def list_orders(self, request):
        store_id = request.query_params.get('store_id')
        if not store_id:
            return Response({'error': 'store_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        store = get_object_or_404(Store, id=store_id)
        orders = Order.objects.filter(store=store).prefetch_related('items').order_by('-created_at')

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(orders, request)

        if page is not None:
            serializer = OrderSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='(?P<order_id>[^/.]+)')
    def retrieve_order(self, request, order_id=None):
        order = get_object_or_404(Order, id=order_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
