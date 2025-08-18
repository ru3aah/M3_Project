from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    image = models.ImageField(
        upload_to="profile_images/",
        null=True,
        blank=True,
        default="profile_images/Default.png",
    )

    phone = models.CharField(max_length=15, null=True, blank=True)

    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
