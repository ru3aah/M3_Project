from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods, require_POST

from products.models import Product
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
            if "manual_quantity" in request.POST:
                quantity = int(request.POST.get("manual_quantity", 1))
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

    # Normalize/validate payment method
    allowed = {c for c, _ in PaymentMethod.choices}
    pm = (
        data.get("payment_method")
        or request.POST.get("payment_method")
        or PaymentMethod.CARD
    )
    # map 'debit' value from template to PaymentMethod.CARD
    if pm == "debit":
        pm = PaymentMethod.CARD
    if pm not in allowed:
        pm = PaymentMethod.CARD

    # Build requested quantities from cart
    requested = {}  # product_id -> (product_obj, requested_qty)
    for line in cart:
        product = line["product"]
        qty = int(line.get("quantity", line.get("data", {}).get("quantity", 0)))
        if qty > 0:
            requested[product.id] = (product, qty)

    if not requested:
        messages.error(request, "Your cart is empty.")
        return redirect("orders:cart_detail")

    any_partial = False
    any_unavailable = False

    with transaction.atomic():
        # Lock products while we validate quantities
        products_map = (
            Product.objects.select_for_update()
            .filter(id__in=list(requested.keys()))
            .in_bulk()
        )

        for pid, (cart_product, req_qty) in requested.items():
            p = products_map.get(pid)

            if not p or int(p.stock or 0) <= 0:
                # Remove from cart
                cart.remove(pid)
                any_unavailable = True
                # Try to use the product's name if available
                removed_name = (p and p.name) or cart_product.name
                messages.warning(
                    request,
                    f"'{removed_name}' is no longer available and was removed from your cart.",
                )
                continue

            current_stock = int(p.stock)
            if req_qty > current_stock:
                any_partial = True
                # If some stock remains, set cart qty to remaining; else remove
                if current_stock > 0:
                    cart.set_quantity(pid, current_stock)
                    messages.info(
                        request,
                        f"Quantity for '{p.name}' was reduced to "
                        f"{current_stock} due to limited stock.",
                    )
                else:
                    cart.remove(pid)
                    any_unavailable = True
                    messages.warning(
                        request,
                        f"'{p.name}' is out of stock and was removed from "
                        f"your cart.",
                    )

        # If anything changed, stop here and send the user to the cart to review.
        if any_unavailable or any_partial:
            if any_unavailable:
                messages.warning(request, "Some items were removed due to no " "stock.")
            if any_partial:
                messages.info(
                    request,
                    "Some item quantities were adjusted to match available " "stock.",
                )
            return redirect("orders:cart_detail")

        # Everything is fully available -> create order and subtract stock.
        order = Order.objects.create(
            user=request.user,
            status=OrderStatus.PENDING,
            total_price=Decimal("0.00"),
            shipping_address=addr,
            payment_method=pm,
        )

        items = []
        subtotal = Decimal("0.00")
        touched = []

        for pid, (cart_product, req_qty) in requested.items():
            p = products_map[pid]  # guaranteed present and sufficient stock
            unit_price = Decimal(str(p.price))
            items.append(
                OrderItem(order=order, product=p, price=unit_price, quantity=req_qty)
            )
            subtotal += unit_price * Decimal(req_qty)
            p.stock = int(p.stock) - req_qty
            touched.append(p)

        OrderItem.objects.bulk_create(items)
        if touched:
            Product.objects.bulk_update(touched, ["stock"])

        # Snapshot address and save totals
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

    # Clear cart after successful order creation
    cart.clear()
    return redirect("orders:order_details", order_id=order.id)


@login_required(login_url="users:login")
def order_success(request, order_id: int):
    # Retained for compatibility if linked elsewhere
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(
        request,
        "orders/order_success.html",
        {
            "order": order,
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M"),
        },
    )


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

    items = order.items.select_related("product").all()

    # Build VM items
    vm_items = []
    subtotal = Decimal("0.00")
    for it in items:
        unit_price = Decimal(str(it.price))
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
        "order": order,
        "order_number": order.id,
        "created_at": order.created_at,
        "total_price": order.total_price,
        "currency": order.currency,
        "status": order.get_status_display(),
        "payment_method_code": order.payment_method,  # 'card' | 'wallet' | 'cod'
        "status_code": order.status,  # 'pending' | 'paid' | ...
        "show_proceed_to_payment": (
            order.status == OrderStatus.PENDING
            and order.payment_method in {PaymentMethod.CARD, PaymentMethod.WALLET}
        ),
        "user_full_name": order.ship_full_name
        or (
            f"{getattr(order.user, 'first_name', '')} "
            f"{getattr(order.user, 'last_name', '')}"
        ).strip(),
        "user_email": getattr(order.user, "email", ""),
        "user_phone": order.ship_recipient_phone or getattr(order.user, "phone", ""),
        "ship_address_line1": order.ship_address_line1,
        "ship_address_line2": order.ship_address_line2,
        "ship_city": order.ship_city,
        "ship_country": order.ship_country,
        "ship_postal_code": order.ship_postal_code,
        "payment_method": order.get_payment_method_display(),
        "items": vm_items,
        "subtotal": subtotal.quantize(Decimal("0.01")),
    }
    return render(request, "orders/order_details.html", context)


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
    """
    Cancel an order. If it transitions to CANCELLED from PENDING or PAID,
    return the allocated stock to products exactly once.
    """
    with transaction.atomic():
        order = (
            Order.objects.select_for_update()
            .prefetch_related("items__product")
            .get(id=order_id, user=request.user)
        )

        if order.status in [OrderStatus.PENDING, OrderStatus.PAID]:
            # Restock products only if not already cancelled
            order.status = OrderStatus.CANCELLED
            order.save(update_fields=["status"])

            # Return stock
            touched = []
            for item in order.items.all():
                p = item.product
                p.stock = int(p.stock) + int(item.quantity)
                touched.append(p)
            if touched:
                Product.objects.bulk_update(touched, ["stock"])

            messages.success(
                request, f"Order #{order.id} has been canceled and stock " f"restored."
            )
        else:
            messages.error(request, "This order cannot be canceled.")

    return redirect("users:account")
