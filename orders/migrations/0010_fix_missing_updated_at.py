from django.db import migrations, models
from django.utils import timezone


def backfill_updated_at(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    # backfill with created_at (or now if created_at is null for some reason)
    for o in Order.objects.all():
        o.updated_at = o.created_at or timezone.now()
        o.save(update_fields=["updated_at"])


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0009_alter_order_options_alter_orderitem_options_and_more"),
    ]

    operations = [
        # 1) add the column allowing NULL so the table can be altered quickly
        migrations.AddField(
            model_name="order",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        # 2) backfill values so we can make it NOT NULL afterwards
        migrations.RunPython(backfill_updated_at, migrations.RunPython.noop),
        # 3) enforce NOT NULL like in your model
        migrations.AlterField(
            model_name="order",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
