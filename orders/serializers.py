from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Handles serialization and deserialization for OrderItem model within the context
    of API communication. The serializer enables transforming OrderItem instances
    into JSON format and validating data for creating or updating OrderItem objects.

    Specifically, this serializer includes a read-only field `product_name` that
    fetches the name of the product related to the order item for representation purposes.

    :ivar product_name: Read-only field that retrieves the name of the associated product
        via the `product.name` relationship.
    :type product_name: serializers.CharField
    """

    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "product_name", "price", "quantity")


class OrderSerializer(serializers.ModelSerializer):
    """
    Represents a serializer for the Order model.

    This serializer is responsible for serializing and deserializing instances of the
    Order model. It includes all essential fields of the Order instance and provides
    serialization for related items through the nested OrderItemSerializer. It ensures
    that operations are consistent and conform to the defined structure.

    :ivar items: A nested serializer for related order items. The items field is read-only
        and allows multiple instances.
    :type items: OrderItemSerializer
    """

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "status", "total_price", "created_at", "items")
