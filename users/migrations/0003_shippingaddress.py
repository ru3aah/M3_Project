# users/migrations/0003_shippingaddress.py
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="shippingaddress",
            name="full_name",
            field=models.CharField(max_length=255, blank=True, default=""),
        ),
    ]
