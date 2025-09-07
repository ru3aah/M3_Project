from django.urls import path

from orders import views
from orders.views import (
    cart_order_add,
    CartDetail,
    cart_order_remove,
    cart_clear,
    checkout,
    order_success,
    order_details,
)

app_name = "orders"

urlpatterns = [
    path("cart/", CartDetail.as_view(), name="cart_detail"),
    path("cart/add/<int:product_id>/", cart_order_add, name="cart_add"),
    path("cart/remove/<int:product_id>/", cart_order_remove, name="cart_remove"),
    path("cart/clear/", cart_clear, name="cart_clear"),
    path("checkout/", checkout, name="checkout"),
    path("order-success/<int:order_id>/", order_success, name="order_success"),
    path("orders/<int:order_id>/", order_details, name="order_details"),
    path("<int:order_id>/pay/", views.pay_order, name="pay_order"),
    path("<int:order_id>/cancel/", views.cancel_order, name="cancel_order"),
]
