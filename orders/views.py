from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods

from .cart import Cart
from .forms import CheckoutForm
from .models import (
    Order,
    OrderItem,
    OrderStatus,
    PaymentMethod,
)


class CartDetail(TemplateView):
    template_name = "orders/cart_detail.html"


@require_http_methods(["POST"])
def cart_order_add(request, product_id: int):
    """
    Add / set / change quantity for a product in the cart.
    Supports:
      - action=increase
      - action=decrease
      - action=set_quantity (legacy 'quantity' field)
      - manual_quantity from the cart input field
      - default 'add' (if no action & not present)
    """
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
            # Support manual quantity from the cart input
            if "manual_quantity" in request.POST:
                quantity = int(request.POST.get("manual_quantity", 1))
                cart.set_quantity(product_id, quantity)
            else:
                # No action parameter – act like "Add to Cart" once
                if product_id not in cart:
                    cart.add(product_id)
    except (TypeError, ValueError):
        # Ignore bad user input and redirect back
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


@login_required(login_url="users:login")
@require_http_methods(["GET", "POST"])
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.info(request, "Your cart is empty.")
        return redirect("orders:cart_detail")

    if request.method == "GET":
        return render(
            request,
            "orders/checkout.html",
            {"cart": cart, "form": CheckoutForm(user=request.user)},
        )

    form = CheckoutForm(request.POST, user=request.user)
    if not form.is_valid():
        return render(request, "orders/checkout.html", {"cart": cart, "form": form})

    data = form.cleaned_data
    addr = data["shipping_address"]

    allowed = {c for c, _ in PaymentMethod.choices}
    pm = (
        data.get("payment_method")
        or request.POST.get("payment_method")
        or PaymentMethod.CARD
    )
    if pm not in allowed:
        pm = PaymentMethod.CARD

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            status=OrderStatus.PENDING,
            total_price=Decimal("0.00"),  # set after items
            shipping_address=addr,
            payment_method=pm,
        )

        # Build items + subtotal (always from DB price)
        items, subtotal = [], Decimal("0.00")
        for line in cart:
            product = line["product"]
            qty = int(line.get("quantity", line.get("data", {}).get("quantity", 0)))
            unit = Decimal(str(product.price))
            items.append(
                OrderItem(order=order, product=product, price=unit, quantity=qty)
            )
            subtotal += unit * Decimal(qty)

        OrderItem.objects.bulk_create(items)
        order.snap_shipping_address(addr)
        order.total_price = subtotal.quantize(Decimal("0.01"))
        order.save(
            update_fields=[
                "ship_full_name",
                "ship_recipient_phone",
                "ship_address_line1",
                "ship_address_line2",
                "ship_city",
                "ship_country",
                "ship_postal_code",
                "total_price",
            ]
        )

        # Minimal user update
        full = (data.get("full_name") or "").strip().split()
        if full:
            request.user.first_name = full[0]
            request.user.last_name = " ".join(full[1:]) if len(full) > 1 else ""
        phone = data.get("phone")
        if phone:
            setattr(request.user, "phone", phone)
        request.user.save(update_fields=["first_name", "last_name", "phone"])

        cart.clear()

    return redirect("orders:order_success", order_id=order.id)


@login_required(login_url="users:login")
def order_success(request, order_id: int):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/order_success.html", {"order": order})


def _update_user_from_checkout(user, full_name: str, phone: str) -> None:
    """Update User.first_name, User.last_name, and User.phone from checkout data."""
    changed = False
    if full_name:
        parts = full_name.strip().split()
        first_name = parts[0]
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
        if user.first_name != first_name:
            user.first_name = first_name
            changed = True
        if user.last_name != last_name:
            user.last_name = last_name
            changed = True
    if phone and getattr(user, "phone", None) != phone:
        user.phone = phone
        changed = True
    if changed:
        user.save()
