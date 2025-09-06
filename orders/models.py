from django.contrib.auth import get_user_model
from django.db import models
from products.models import JournalizedModel
from users.models import ShippingAddress


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    SHIPPED = "shipped", "Shipped"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = "cancelled", "Cancelled"


class PaymentMethod(models.TextChoices):
    CARD = "card", "Debit Card"
    WALLET = "wallet", "Digital Wallet"
    COD = "cod", "Cash on Delivery"


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

    ship_full_name = models.CharField(max_length=255, blank=True, default="")
    ship_recipient_phone = models.CharField(max_length=15, blank=True, default="")
    ship_address_line1 = models.CharField(max_length=255, blank=True, default="")
    ship_address_line2 = models.CharField(max_length=255, blank=True, default="")
    ship_city = models.CharField(max_length=255, blank=True, default="")
    ship_country = models.CharField(max_length=255, blank=True, default="")
    ship_postal_code = models.CharField(max_length=8, blank=True, default="")

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod,
        default=PaymentMethod.CARD,
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=OrderStatus,
        default=OrderStatus.PENDING,
        db_index=True,
    )

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    currency = models.CharField(max_length=3, default="USD")

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.id}"

    def snap_shipping_address(self, addr: ShippingAddress | None):
        """
        Копирует данные адреса (и ФИО/телефон пользователя) в snapshot-поля.
        Используй в checkout view ПЕРЕД сохранением заказа.
        """
        first_name = (getattr(self.user, "first_name", "") or "").strip()
        last_name = (getattr(self.user, "last_name", "") or "").strip()
        self.ship_full_name = f"{first_name} {last_name}".strip()

        self.ship_recipient_phone = (getattr(self.user, "phone", "") or "").strip()

        if addr:
            self.ship_address_line1 = addr.address_line_1 or ""
            self.ship_address_line2 = addr.address_line_2 or ""
            self.ship_city = addr.city or ""
            self.ship_country = addr.country or ""
            self.ship_postal_code = addr.postal_code or ""
        else:
            self.ship_address_line1 = ""
            self.ship_address_line2 = ""
            self.ship_city = ""
            self.ship_country = ""
            self.ship_postal_code = ""


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    price = models.DecimalField(
        max_digits=10, decimal_places=2
    )  # цена на момент покупки
    quantity = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.id}: {self.quantity} x {self.product.name}"
