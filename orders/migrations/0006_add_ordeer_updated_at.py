from django.db import migrations, models
from django.utils import timezone


def backfill_updated_at(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    now = timezone.now()
    for o in Order.objects.all().only("pk", "created_at"):
        Order.objects.filter(pk=o.pk).update(updated_at=o.created_at or now)


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0005_alter_order_options_alter_orderitem_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True, blank=True),
        ),
        migrations.RunPython(backfill_updated_at, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="order",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
