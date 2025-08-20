from django.contrib.auth import get_user_model
from django.db import models

from products.models import JournalizedModel


class Order(JournalizedModel):
    STATUSES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUSES, default="pending")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField(max_length=500)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
