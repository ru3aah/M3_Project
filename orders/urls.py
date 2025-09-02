from django.urls import path

from orders.views import (
    cart_order_add,
    CartDetail,
    cart_order_remove,
    cart_clear,
    checkout,
    order_success,
)

app_name = "orders"

urlpatterns = [
    path("cart/", CartDetail.as_view(), name="cart_detail"),
    path("cart/add/<int:product_id>/", cart_order_add, name="cart_add"),
    path("cart/remove/<int:product_id>/", cart_order_remove, name="cart_remove"),
    path("cart/clear/", cart_clear, name="cart_clear"),
    path("checkout/", checkout, name="checkout"),
    path("order-success/<int:order_id>/", order_success, name="order_success"),
]
