import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.products.models import Category, Product, Store, Inventory

pytestmark = pytest.mark.django_db


class TestProductAPI:
    def setup_method(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            title='Laptop',
            description='High-end laptop',
            price=1299.99,
            category=self.category
        )

    def test_list_products(self):
        response = self.client.get('/api/products/products/')
        assert response.status_code == 200
        assert 'results' in response.data or isinstance(response.data, list)

    def test_retrieve_product(self):
        response = self.client.get(f'/api/products/products/{self.product.id}/')
        assert response.status_code == 200
        assert response.data['title'] == 'Laptop'

    def test_search_products_by_title(self):
        response = self.client.get('/api/products/products/?search=Laptop')
        assert response.status_code == 200

    def test_filter_by_category(self):
        response = self.client.get(f'/api/products/products/?category={self.category.id}')
        assert response.status_code == 200


class TestInventoryAPI:
    def setup_method(self):
        self.client = APIClient()
        self.store = Store.objects.create(name='Store 1', location='Location 1')
        self.category = Category.objects.create(name='Books')
        self.product = Product.objects.create(
            title='Django Book',
            description='Learn Django',
            price=45.99,
            category=self.category
        )
        self.inventory = Inventory.objects.create(
            store=self.store,
            product=self.product,
            quantity=30
        )

    def test_list_inventory(self):
        response = self.client.get(f'/api/products/stores/{self.store.id}/inventory/')
        assert response.status_code == 200
        assert len(response.data) > 0 or 'results' in response.data


class TestCategoryAPI:
    def setup_method(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Home')

    def test_list_categories(self):
        response = self.client.get('/api/products/categories/')
        assert response.status_code == 200

    def test_retrieve_category(self):
        response = self.client.get(f'/api/products/categories/{self.category.id}/')
        assert response.status_code == 200
        assert response.data['name'] == 'Home'
