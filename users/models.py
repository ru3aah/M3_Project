from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    image = models.ImageField(
        upload_to="profile_images/",
        null=True,
        blank=True,
        default="profile_images/Default.png",
    )
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return self.email or self.username


class ShippingAddress(models.Model):
    """
    Адрес доставки, привязан к пользователю.
    Поле default позволяет хранить "адрес по умолчанию".
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shipping_addresses",
    )
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=8)
    default = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Shipping Address"
        verbose_name_plural = "Shipping Addresses"
        indexes = [
            models.Index(fields=["user", "default"]),
        ]

    def __str__(self) -> str:
        parts = [self.address_line_1]
        if self.address_line_2:
            parts.append(self.address_line_2)
        parts += [self.postal_code, self.city, self.country]
        return ", ".join([p for p in parts if p])
