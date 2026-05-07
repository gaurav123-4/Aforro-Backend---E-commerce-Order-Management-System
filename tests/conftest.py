import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aforro_project.settings')

if not settings.configured:
    django.setup()

import pytest
from django.test.client import Client
from apps.products.models import Category, Product, Store, Inventory
from apps.orders.models import Order, OrderItem


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def category():
    return Category.objects.create(name='Test Category')


@pytest.fixture
def product(category):
    return Product.objects.create(
        title='Test Product',
        description='Test Description',
        price=99.99,
        category=category
    )


@pytest.fixture
def store():
    return Store.objects.create(
        name='Test Store',
        location='Test Location'
    )


@pytest.fixture
def inventory(store, product):
    return Inventory.objects.create(
        store=store,
        product=product,
        quantity=50
    )


@pytest.fixture
def order(store):
    return Order.objects.create(
        store=store,
        status='PENDING'
    )


@pytest.fixture
def order_item(order, product):
    return OrderItem.objects.create(
        order=order,
        product=product,
        quantity_requested=5
    )
