import pytest
from rest_framework.test import APIClient
from apps.products.models import Category, Product

pytestmark = pytest.mark.django_db


class TestSearchAPI:
    def setup_method(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Books')
        self.product1 = Product.objects.create(
            title='Django for Beginners',
            description='Learn Django basics',
            price=29.99,
            category=self.category
        )
        self.product2 = Product.objects.create(
            title='Advanced Django',
            description='Master Django patterns',
            price=49.99,
            category=self.category
        )

    def test_search_products_by_keyword(self):
        response = self.client.get('/api/search/products/?q=Django')
        assert response.status_code == 200
        assert 'results' in response.data or len(response.data) > 0

    def test_search_products_with_price_filter(self):
        response = self.client.get('/api/search/products/?q=Django&price_min=25&price_max=40')
        assert response.status_code == 200

    def test_search_products_sorted_by_price(self):
        response = self.client.get('/api/search/products/?sort_by=price')
        assert response.status_code == 200

    def test_autocomplete(self):
        response = self.client.get('/api/search/suggest/?q=Djan')
        assert response.status_code == 200
        assert 'suggestions' in response.data

    def test_autocomplete_short_query(self):
        response = self.client.get('/api/search/suggest/?q=D')
        assert response.status_code == 200
        assert response.data['suggestions'] == []
