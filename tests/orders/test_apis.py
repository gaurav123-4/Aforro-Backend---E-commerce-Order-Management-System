import pytest
import json
from rest_framework.test import APIClient
from apps.products.models import Category, Product, Store, Inventory
from apps.orders.models import Order, OrderItem

pytestmark = pytest.mark.django_db


class TestOrderAPI:
    def setup_method(self):
        self.client = APIClient()
        self.store = Store.objects.create(name='Test Store', location='Test Location')
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            title='Test Product',
            description='Test Product Description',
            price=99.99,
            category=self.category
        )
        self.inventory = Inventory.objects.create(
            store=self.store,
            product=self.product,
            quantity=100
        )

    def test_create_order_success(self):
        payload = {
            'store_id': self.store.id,
            'items': [
                {
                    'product_id': self.product.id,
                    'quantity_requested': 5
                }
            ]
        }
        response = self.client.post(
            '/api/orders/create_order/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 201
        assert response.data['status'] == 'CONFIRMED'

    def test_create_order_insufficient_stock(self):
        self.inventory.quantity = 2
        self.inventory.save()

        payload = {
            'store_id': self.store.id,
            'items': [
                {
                    'product_id': self.product.id,
                    'quantity_requested': 5
                }
            ]
        }
        response = self.client.post(
            '/api/orders/create_order/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert 'error' in response.data

    def test_list_orders(self):
        Order.objects.create(store=self.store, status='CONFIRMED')
        response = self.client.get(f'/api/orders/list_orders/?store_id={self.store.id}')
        assert response.status_code == 200

    def test_retrieve_order(self):
        order = Order.objects.create(store=self.store, status='CONFIRMED')
        response = self.client.get(f'/api/orders/{order.id}/')
        assert response.status_code == 200
        assert response.data['status'] == 'CONFIRMED'
