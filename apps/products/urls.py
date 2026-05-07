from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.products.views import CategoryViewSet, ProductViewSet, StoreViewSet, InventoryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'stores', StoreViewSet)

inventory_list = InventoryViewSet.as_view({'get': 'list'})

urlpatterns = [
    path('', include(router.urls)),
    path('stores/<int:store_id>/inventory/', inventory_list, name='inventory-list'),
]
