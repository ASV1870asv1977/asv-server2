

from mainapp.models import Product
from ordersapp.models import OrderItem

from django.core.management import BaseCommand
from django.db.models import F, When, Case, DecimalField, IntegerField, Q

from datetime import timedelta


class Command(BaseCommand):

    def handle(self, *args, **options):

        # ----------- 1 --------------------
        # query_1 = Q(category__name='офис')
        # query_2 = Q(category__name='дом')
        # products_list = Product.objects.filter(query_1 | query_2)
        # print(products_list.values_list('category__name', flat=True))

        # ----------- 2 --------------------
        action_1 = 1  # 30%
        action_2 = 2  # 10%
        action_3 = 3  # 5%

        action_1_time_delta = timedelta(hours=12)
        action_2_time_delta = timedelta(days=1)

        action_1_discount = 0.3
        action_2_discount = 0.15
        action_3_discount = 0.05

        action_1_condition = Q(order__updated__lte=F('order__created') + action_1_time_delta)
        action_2_condition = Q(order__updated__lte=F('order__created') + action_2_time_delta) &\
                             Q(order__updated__gt=F('order__created') + action_1_time_delta)
        action_3_condition = Q(order__updated__gt=F('order__created') + action_2_time_delta)

        action_1_order = When(action_1_condition, then=action_1)
        action_2_order = When(action_2_condition, then=action_2)
        action_3_order = When(action_3_condition, then=action_3)

        action_1_price = When(action_1_condition, then=F('product__price') * F('quantity') * action_1_discount)
        action_2_price = When(action_2_condition, then=F('product__price') * F('quantity') * action_2_discount)
        action_3_price = When(action_3_condition, then=F('product__price') * F('quantity') * action_3_discount)

        order_items_list = OrderItem.objects.annotate(
            action_order=Case(
                action_1_order,
                action_2_order,
                action_3_order,
                output_field=IntegerField()
            )
        ).annotate(
            total_price=Case(
                action_1_price,
                action_2_price,
                action_3_price,
                output_field=DecimalField()
            )
        ).order_by('action_order', 'total_price').select_related()

        for order_item in order_items_list:
            print(f'{order_item.action_order:2}: order #: {order_item.pk:4}: '
                  f'product: {order_item.product.name:20}: discount: {order_item.total_price:8.2f} rub '
                  f'{order_item.order.updated - order_item.order.created}')




# ACTION_1 = 1
# ACTION_2 = 2
# ACTION_EXPIRED = 3
#
# action_1__time_delta = timedelta(hours=12)
# action_2__time_delta = timedelta(days=1)
#
# action_1__discount = 0.3
# action_2__discount = 0.15
# action_expired__discount = 0.05
#
# action_1__condition = Q(order__updated__lte=F('order__created') + action_1__time_delta)
#
# action_2__condition = Q(order__updated__gt=F('order__created') + action_1__time_delta) & \
#                       Q(order__updated__lte=F('order__created') + action_2__time_delta)
#
# action_expired__condition = Q(order__updated__gt=F('order__created') + action_2__time_delta)
#
# action_1__order = When(action_1__condition, then=ACTION_1)
# action_2__order = When(action_2__condition, then=ACTION_2)
# action_expired__order = When(action_expired__condition, then=ACTION_EXPIRED)
#
# action_1__price = When(action_1__condition, then=F('product__price') * F('quantity') * action_1__discount)
#
# action_2__price = When(action_2__condition, then=F('product__price') * F('quantity') * -action_2__discount)
#
# action_expired__price = When(action_expired__condition,
#                              then=F('product__price') * F('quantity') * action_expired__discount)
#
# test_orderss = OrderItem.objects.annotate(
#     action_order=Case(
#         action_1__order,
#         action_2__order,
#         action_expired__order,
#         output_field=IntegerField(),
#     )).annotate(
#     total_price=Case(
#         action_1__price,
#         action_2__price,
#         action_expired__price,
#         output_field=DecimalField(),
#     )).order_by('action_order', 'total_price').select_related()
#
# for orderitem in test_orderss:
#     print(f'{orderitem.action_order:2}: заказ №{orderitem.pk:3}:\
#            {orderitem.product.name:15}: скидка\
#            {abs(orderitem.total_price):6.2f} руб. | \
#            {orderitem.order.updated - orderitem.order.created}')
