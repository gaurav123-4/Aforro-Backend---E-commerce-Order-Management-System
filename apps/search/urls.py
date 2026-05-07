from django.urls import path
from apps.search.views import SearchViewSet

search_products = SearchViewSet.as_view({'get': 'search_products'})
search_suggest = SearchViewSet.as_view({'get': 'autocomplete'})

urlpatterns = [
    path('products/', search_products, name='search-products'),
    path('suggest/', search_suggest, name='autocomplete'),
]
