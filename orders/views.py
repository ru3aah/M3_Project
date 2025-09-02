from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import TemplateView

from orders.cart import Cart
from django.views.decorators.http import require_http_methods
from .models import Order, OrderItem, OrderStatus


class CartDetail(TemplateView):
    template_name = "orders/cart_detail.html"


@require_http_methods(["POST"])
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
            if "manual_quantity" in request.POST:
                quantity = int(request.POST.get("manual_quantity"))
                cart.set_quantity(product_id, quantity)
            else:
                if product_id not in cart:
                    cart.add(product_id)
    except (TypeError, ValueError):
        pass

    next_url = request.GET.get("next")
    return redirect(next_url or "orders:cart_detail")


@require_http_methods(["POST"])
def cart_order_remove(request, product_id: int):
    cart = Cart(request)
    cart.remove(product_id)
    next_url = request.GET.get("next")
    return redirect(next_url or "orders:cart_detail")


@require_http_methods(["POST"])
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("orders:cart_detail")


@require_http_methods(["GET", "POST"])
@login_required(login_url="users:login")
def checkout(request):
    """
    Requires login. On GET: show summary + shipping form.
    On POST: create Order + OrderItems from the Cart, then clear Cart, redirect to success.
    Assumes your Order has: user, status, total_price, shipping_address
    and your OrderItem has: order, product, price, quantity
    """
    cart = Cart(request)
    if len(cart) == 0:
        messages.info(request, "Your cart is empty.")
        return redirect("orders:cart_detail")

    if request.method == "POST":
        # Minimal shipping capture (adjust to your forms if you already have one)
        shipping_address = (request.POST.get("shipping_address") or "").strip()
        if not shipping_address:
            messages.error(request, "Please provide a shipping address.")
            return render(request, "orders/checkout.html", {"cart": cart})

        # Create order atomically
        with transaction.atomic():
            total_price = cart.get_total_price()
            order = Order.objects.create(
                user=request.user,
                status=OrderStatus.PENDING,
                total_price=total_price,
                shipping_address=shipping_address,
            )

            # Cart iterator is expected to yield dicts with product/price/quantity
            for line in cart:
                product = line["product"]
                unit_price = line["price"]
                qty = line["quantity"]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=unit_price,  # snapshot
                    quantity=qty,
                )

            cart.clear()

        return redirect("orders:order_success", order_id=order.id)

    # GET
    return render(request, "orders/checkout.html", {"cart": cart})


@login_required(login_url="users:login")
def order_success(request, order_id: int):
    # Optional: restrict to owner if needed
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/order_success.html", {"order": order})
