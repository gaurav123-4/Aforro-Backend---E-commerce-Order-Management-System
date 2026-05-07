from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_order_async(order_id):
    from apps.orders.models import Order
    try:
        order = Order.objects.get(id=order_id)
        logger.info(f'Processing order {order_id} - Status: {order.status}')
        return f'Order {order_id} processed successfully'
    except Order.DoesNotExist:
        logger.error(f'Order {order_id} not found')
        return f'Order {order_id} not found'
    except Exception as e:
        logger.error(f'Error processing order {order_id}: {str(e)}')
        return f'Error processing order {order_id}'
