from django.contrib.auth import get_user_model
from django.db import models
from products.models import JournalizedModel


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
    status = models.CharField(
        max_length=20, choices=OrderStatus, default=OrderStatus.PENDING, db_index=True
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField(max_length=500)

    def __str__(self):
        return f"Order {self.id}"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.id}: {self.quantity} x {self.product.name}"

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
