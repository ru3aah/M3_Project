from django.urls import path

from orders.views import cart_order_add, CartDetail, cart_order_remove, cart_clear

app_name = "orders"

urlpatterns = [
    path("cart/add/<int:product_id>/", cart_order_add, name="cart_add"),
    path("cart/", CartDetail.as_view(), name="cart_detail"),
    path("cart/remove/<int:product_id>/", cart_order_remove, name="cart_remove"),
    path("cart/clear/", cart_clear, name="cart_clear"),
]
