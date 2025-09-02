from django.shortcuts import redirect
from django.views.generic import TemplateView
from orders.cart import Cart


class CartDetail(TemplateView):
    template_name = "orders/cart_detail.html"


def cart_order_add(request, product_id: int):
    cart = Cart(request)
    action = request.POST.get("action")

    try:
        if action == "increase":
            cart.increase_quantity(product_id)
        elif action == "decrease":
            cart.decrease_quantity(product_id)
        elif action == "set_quantity":
            quantity = int(request.POST.get("quantity", 1))
            cart.set_quantity(product_id, quantity)
        else:
            # No action parameter - this is the "Add to Cart" button
            # Only add if not already in cart, otherwise do nothing
            if product_id not in cart:
                cart.add(product_id)
    except (TypeError, ValueError):
        pass

    next_url = request.GET.get("next")
    return redirect(next_url or "orders:cart_detail")


def cart_order_remove(request, product_id: int):
    cart = Cart(request)
    cart.remove(product_id)
    next_url = request.GET.get("next")
    return redirect(next_url or "orders:cart_detail")


def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("orders:cart_detail")
