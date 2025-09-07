from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods, require_POST

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

    return redirect("orders:order_details", order_id=order.id)


@login_required(login_url="users:login")
def order_success(request, order_id: int):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(
        request,
        "orders/order_success.html",
        {
            "order": order,
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M"),
        },
    )


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


@login_required(login_url="users:login")
def order_details(request, order_id: int):
    """
    Detailed order page:
      1) Order header: number, date, total, currency, status
      2) User details
      3) Shipping address (snapshot)
      4) Payment method
      5) Item list with product, unit price, qty, measure unit, line subtotal
    """
    order = get_object_or_404(
        Order.objects.select_related("user", "shipping_address"),
        id=order_id,
        user=request.user,
    )

    # Fetch items + products in one go
    items = order.items.select_related("product").all()

    # Build a lightweight items view model with safe fallbacks
    vm_items = []
    subtotal = Decimal("0.00")
    for it in items:
        unit_price = Decimal(str(it.price))  # unit price at time of purchase
        qty = int(it.quantity)
        line_total = (unit_price * Decimal(qty)).quantize(Decimal("0.01"))

        product = it.product
        measure_unit = (
            getattr(product, "measuring_unit", None)
            or getattr(product, "measure_unit", None)
            or getattr(product, "unit", None)
            or ""
        )

        vm_items.append(
            {
                "name": getattr(
                    product, "name", f"Product #{getattr(product, 'id', '')}"
                ),
                "unit_price": unit_price,
                "quantity": qty,
                "measure_unit": measure_unit,
                "line_total": line_total,
            }
        )
        subtotal += line_total

    context = {
        # 1) Order header
        "order": order,
        "order_number": order.id,
        "created_at": order.created_at,  # use |date in template
        "total_price": order.total_price,
        "currency": order.currency,
        "status": order.get_status_display(),  # human label
        # expose raw codes (lowercase, per models.py)
        "payment_method_code": order.payment_method,  # 'card' | 'wallet' | 'cod'
        "status_code": order.status,  # 'pending' | 'paid' | ...
        # convenience boolean for the template
        "show_proceed_to_payment": (
            order.status == OrderStatus.PENDING
            and order.payment_method in {PaymentMethod.CARD, PaymentMethod.WALLET}
        ),
        # 2) User details
        "user_full_name": order.ship_full_name
        or (
            f"{getattr(order.user, 'first_name', '')} {getattr(order.user, 'last_name', '')}"
        ).strip(),
        "user_email": getattr(order.user, "email", ""),
        "user_phone": order.ship_recipient_phone or getattr(order.user, "phone", ""),
        # 3) Shipping address snapshot (from order)
        "ship_address_line1": order.ship_address_line1,
        "ship_address_line2": order.ship_address_line2,
        "ship_city": order.ship_city,
        "ship_country": order.ship_country,
        "ship_postal_code": order.ship_postal_code,
        # 4) Payment method
        "payment_method": order.get_payment_method_display(),
        # 5) Items
        "items": vm_items,
        "subtotal": subtotal.quantize(Decimal("0.01")),
    }
    return render(request, "orders/order_details.html", context)


@login_required(login_url="users:login")
def order_success(request, order_id: int):
    """
    Keep existing route working, but show the new details page.
    """
    return redirect("orders:order_details", order_id=order_id)


@login_required(login_url="users:login")
@require_POST
def pay_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != OrderStatus.PENDING:
        messages.error(request, "Only pending orders can be paid.")
    else:
        order.status = OrderStatus.PAID
        order.save(update_fields=["status"])
        messages.success(request, f"Order #{order.id} has been paid.")

    return redirect("users:account")


@login_required(login_url="users:login")
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status not in [OrderStatus.PENDING, OrderStatus.PAID]:
        messages.error(request, "This order cannot be canceled.")
    else:
        order.status = OrderStatus.CANCELLED
        order.save(update_fields=["status"])
        messages.success(request, f"Order #{order.id} has been canceled.")

    return redirect("users:account")
