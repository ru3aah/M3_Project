from __future__ import annotations

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

from .models import Order, OrderStatus, PaymentMethod


def _build_order_url(order: Order) -> str:
    """
    Build an absolute URL to the order details page for emails.
    """
    base = getattr(settings, "SITE_URL", "").rstrip("/")
    try:
        path = reverse("orders:order_details", args=[order.id])
    except Exception:
        path = f"/orders/{order.id}/"
    return f"{base}{path}" if base else path


def _label_from_choice(choices, code: str | None) -> str:
    """
    Get the human-readable label from a Django TextChoices enum, falling back to the code.
    """
    if not code:
        return ""
    mapping = dict(choices)
    return mapping.get(code, code)


def send_order_status_email_html(
    to_email: str,
    order: Order,
    *,
    old_status: str | None,
    is_created: bool,
) -> None:
    """
    Sends a multipart (text + HTML) email about order creation or status changes.
    """
    if not to_email:
        return

    #  labels
    status_label = order.get_status_display()
    old_status_label = (
        _label_from_choice(OrderStatus.choices, old_status) if old_status else None
    )
    payment_method_label = order.get_payment_method_display()

    # Context for templates
    context = {
        "order": order,
        "order_id": order.id,
        "status_label": status_label,
        "old_status_label": old_status_label,
        "is_created": is_created,
        "total_price": order.total_price,
        "currency": order.currency,
        "created_at": order.created_at,
        "payment_method_label": payment_method_label,
        "payment_method_code": order.payment_method,  # 'card' | 'wallet' | 'cod'
        "order_url": _build_order_url(order),
        "site_name": "Hop & Barley",
        "support_email": getattr(
            settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"
        ),
        # Useful flags
        "can_pay_now": (
            order.status == OrderStatus.PENDING
            and order.payment_method in {PaymentMethod.CARD, PaymentMethod.WALLET}
        ),
    }

    subject = f"Order #{order.id} – {status_label}"

    text_body = render_to_string("emails/order_status.txt", context)
    html_body = render_to_string("emails/order_status.html", context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
        to=[to_email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=True)
