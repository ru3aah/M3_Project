from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    image = models.ImageField(
        upload_to="profile_images/",
        null=True,
        blank=True,
        default="profile_images/Default.png",
    )
    phone = models.CharField(max_length=32, null=True, blank=True)
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email


class ShippingAddress(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=8)
    default = models.BooleanField(default=False)
