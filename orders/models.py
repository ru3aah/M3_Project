from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models

from config.settings import DEFAULT_AUTO_FIELD
from products.models import JournalizedModel
from users.models import ShippingAddress


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    SHIPPED = "shipped", "Shipped"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = "cancelled", "Cancelled"


class Order(JournalizedModel):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="orders",
        null=True,
        blank=True,
    )
    shipping_address = models.ForeignKey(
        ShippingAddress,
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
    )
    # shipping address snapshot
    ship_full_name = models.CharField(max_length=255, blank=True, default="")
    ship_recipient_phone = models.CharField(max_length=32, blank=True, default="")
    ship_address_line1 = models.CharField(max_length=255, blank=True, default="")
    ship_address_line2 = models.CharField(max_length=255, blank=True, default="")
    ship_city = models.CharField(max_length=255, blank=True, default="")
    ship_country = models.CharField(max_length=255, blank=True, default="")
    ship_postal_code = models.CharField(max_length=20, blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        db_index=True,
    )

    currency = models.CharField(max_length=3, default="USD")
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    def __str__(self):
        return f"Order {self.id}"

    def snap_shipping_address(self, addr: ShippingAddress):
        ship_full_name = ""
        if self.user:
            first_name = getattr(self.user, "first_name", "") or ""
            last_name = getattr(self.user, "last_name", "") or ""
            ship_full_name = f"{first_name} {last_name}".strip()

        self.ship_full_name = ship_full_name or ""
        self.ship_recipient_phone = (getattr(self.user, "phone", "") or "").strip()
        self.ship_address_line1 = addr.address_line_1 or ""
        self.ship_address_line2 = addr.address_line_2 or ""
        self.ship_city = addr.city or ""
        self.ship_country = addr.country or ""
        self.ship_postal_code = addr.postal_code or ""

    def recalc_totals(self, save: bool = True):
        """Recalculate order total price. The currency is taken from the
        first product."""
        items = list(self.items.select_related("product"))
        total = Decimal("0.00")
        order_currency = self.currency or None

        for it in items:
            total += (it.price or Decimal("0.00")) * Decimal(it.quantity or 0)
            if (
                not order_currency
                and hasattr(it.product, "currency")
                and it.product.currency
            ):
                order_currency = it.product.currency

        self.total_price = total
        if order_currency:
            self.currency = order_currency

        if save:
            self.save(update_fields=["total_price", "currency", "updated_at"])

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "products.Product", on_delete=models.PROTECT, related_name="order_items"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Unit price at the time of order creation.",
    )
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.id}: {self.quantity} x {self.product.name}"

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["product"]),
        ]

    constraints = [
        models.CheckConstraint(
            check=models.Q(quantity__gte=0), name="orderitem_qty_gte_0"
        )
    ]


@property
def line_total(self) -> Decimal:
    return (self.price or Decimal("0.00")) * Decimal(self.quantity or 0)
