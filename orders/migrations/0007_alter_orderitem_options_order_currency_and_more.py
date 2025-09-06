# Generated manually to safely convert shipping_address TEXT -> FK and add snapshot fields.
from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


def backfill_currency(apps, schema_editor):
    """
    Проставить валюту заказа из первого товара в заказе, если получится.
    """
    Order = apps.get_model("orders", "Order")
    OrderItem = apps.get_model("orders", "OrderItem")

    for order in Order.objects.all():
        oi = (
            OrderItem.objects.select_related("product")
            .filter(order_id=order.id)
            .order_by("id")
            .first()
        )
        if oi and getattr(oi.product, "currency", None):
            Order.objects.filter(pk=order.pk).update(currency=oi.product.currency)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_alter_user_phone_shippingaddress"),
        # Завязываем 0007 на твою 0006 (имя с опечаткой сохранено как у тебя)
        ("orders", "0006_add_ordeer_updated_at"),
    ]

    operations = [
        # 0) В СТАРОМ состоянии столбец shipping_address ещё TEXT NOT NULL.
        # Сначала делаем его nullable как TEXT, чтобы затем можно было поставить NULL.
        migrations.AlterField(
            model_name="order",
            name="shipping_address",
            field=models.TextField(blank=True, null=True),
        ),
        # 1) Добавляем снапшот-поля адреса доставки
        migrations.AddField(
            model_name="order",
            name="ship_full_name",
            field=models.CharField(max_length=255, blank=True, default=""),
        ),
        migrations.AddField(
            model_name="order",
            name="ship_recipient_phone",
            field=models.CharField(max_length=15, blank=True, default=""),
        ),
        migrations.AddField(
            model_name="order",
            name="ship_address_line1",
            field=models.CharField(max_length=255, blank=True, default=""),
        ),
        migrations.AddField(
            model_name="order",
            name="ship_address_line2",
            field=models.CharField(max_length=255, blank=True, default=""),
        ),
        migrations.AddField(
            model_name="order",
            name="ship_city",
            field=models.CharField(max_length=255, blank=True, default=""),
        ),
        migrations.AddField(
            model_name="order",
            name="ship_country",
            field=models.CharField(max_length=255, blank=True, default=""),
        ),
        migrations.AddField(
            model_name="order",
            name="ship_postal_code",
            field=models.CharField(max_length=8, blank=True, default=""),
        ),
        # 2) Валюта заказа + безопасный дефолт для total_price
        migrations.AddField(
            model_name="order",
            name="currency",
            field=models.CharField(max_length=3, default="USD"),
        ),
        migrations.AlterField(
            model_name="order",
            name="total_price",
            field=models.DecimalField(
                max_digits=10, decimal_places=2, default=Decimal("0.00")
            ),
        ),
        # 3) Теперь можно безопасно очистить старые текстовые значения (они нам не нужны)
        migrations.RunSQL("UPDATE orders_order SET shipping_address = NULL"),
        # 4) И только после этого переводим колонку в FK -> users.ShippingAddress (nullable)
        migrations.AlterField(
            model_name="order",
            name="shipping_address",
            field=models.ForeignKey(
                to="users.ShippingAddress",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="orders",
                null=True,
                blank=True,
            ),
        ),
        # 5) Уточняем поля в OrderItem (как генерила авто-миграция) + индексы
        migrations.AlterField(
            model_name="orderitem",
            name="product",
            field=models.ForeignKey(
                to="products.product",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="order_items",
            ),
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="price",
            field=models.DecimalField(max_digits=10, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="quantity",
            field=models.PositiveIntegerField(),
        ),
        migrations.AddIndex(
            model_name="orderitem",
            index=models.Index(fields=["order"], name="orders_orde_order_i_5d347b_idx"),
        ),
        migrations.AddIndex(
            model_name="orderitem",
            index=models.Index(
                fields=["product"], name="orders_orde_product_32ff41_idx"
            ),
        ),
        # 6) Бест-эффорт: подтянем валюту из товаров
        migrations.RunPython(backfill_currency, migrations.RunPython.noop),
    ]
