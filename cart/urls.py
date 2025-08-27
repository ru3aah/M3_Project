from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.CartView.as_view(), name="cart"),
    path("add/", views.AddToCartView.as_view(), name="add_to_cart"),
    path("update/", views.UpdateCartView.as_view(), name="update_cart"),
    path("remove/", views.RemoveFromCartView.as_view(), name="remove_from_cart"),
]
