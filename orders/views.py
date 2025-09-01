from django.shortcuts import redirect
from django.views.generic import TemplateView
from orders.cart import Cart


class CartDetail(TemplateView):
    template_name = "orders/cart_detail.html"


def cart_order_add(request, product_id: int):
    cart = Cart(request)
    action = request.POST.get("action")
    qty = request.POST.get("quantity")
    try:
        if action in {"increase", "decrease"}:
            cart.change_quantity(product_id, 1 if action == "increase" else -1)
        elif qty is not None:
            cart.change_quantity(product_id, int(qty))
        else:
            cart.change_quantity(product_id, 1)
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
