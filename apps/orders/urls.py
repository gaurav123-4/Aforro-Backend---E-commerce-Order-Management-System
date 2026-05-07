from django.urls import path
from apps.orders.views import OrderViewSet

order_create = OrderViewSet.as_view({'post': 'create_order'})
order_list = OrderViewSet.as_view({'get': 'list_orders'})
order_retrieve = OrderViewSet.as_view({'get': 'retrieve_order'})

urlpatterns = [
    path('create_order/', order_create, name='order-create'),
    path('list_orders/', order_list, name='order-list'),
    path('<int:order_id>/', order_retrieve, name='order-detail'),
]
