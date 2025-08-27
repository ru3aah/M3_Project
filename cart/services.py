from django.conf import settings
from products.models import Product
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError


class CartService:
    """
    Service class to handle shopping cart operations.
    Stores cart data in Django session and manages stock reservations.
    """

    def __init__(self, request):
        """
        Initialize cart service with request session.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add_to_cart(self, product, quantity=1):
        """
        Add a product to the cart with specified quantity.
        Updates database stock to reserve the items.
        """
        product_id = str(product.id)

        with transaction.atomic():
            # Get fresh product data with row-level locking
            fresh_product = Product.objects.select_for_update().get(id=product.id)

            # Get current cart quantity
            current_cart_qty = self.cart.get(product_id, {}).get("quantity", 0)

            # Check if we have enough stock for the new quantity
            if fresh_product.stock < quantity:
                raise ValidationError(
                    f"Only {fresh_product.stock} items available in stock"
                )

            # Update product stock (decrease by the quantity being added)
            fresh_product.stock -= quantity
            fresh_product.save()

            # Update cart
            if product_id not in self.cart:
                self.cart[product_id] = {
                    "quantity": 0,
                    "price": str(product.price),
                    "name": product.name,
                    "image": product.image.url if product.image else None,
                    "unit_measure": product.unit_measure,
                    "currency": product.currency,
                }

            self.cart[product_id]["quantity"] += quantity
            self.save()

    def update_quantity(self, product_id, new_quantity):
        """
        Update the quantity of a product in the cart.
        Adjusts database stock accordingly.
        """
        product_id = str(product_id)

        if product_id not in self.cart:
            return

        with transaction.atomic():
            # Get fresh product data with row-level locking
            fresh_product = Product.objects.select_for_update().get(id=product_id)

            # Get current cart quantity
            current_cart_qty = self.cart[product_id]["quantity"]

            if new_quantity <= 0:
                # Removing item completely - return all quantity to stock
                fresh_product.stock += current_cart_qty
                fresh_product.save()
                del self.cart[product_id]
            else:
                # Calculate the difference
                qty_difference = new_quantity - current_cart_qty

                if qty_difference > 0:
                    # Increasing quantity - check if we have enough stock
                    if fresh_product.stock < qty_difference:
                        raise ValidationError(
                            f"Only {fresh_product.stock} additional items available"
                        )

                    # Decrease stock by the additional quantity
                    fresh_product.stock -= qty_difference
                else:
                    # Decreasing quantity - return some stock
                    fresh_product.stock += abs(qty_difference)

                fresh_product.save()
                self.cart[product_id]["quantity"] = new_quantity

            self.save()

    def remove_from_cart(self, product_id):
        """
        Remove a product from the cart and return its quantity to stock.
        """
        product_id = str(product_id)

        if product_id not in self.cart:
            return

        with transaction.atomic():
            # Get fresh product data with row-level locking
            fresh_product = Product.objects.select_for_update().get(id=product_id)

            # Get current cart quantity
            current_cart_qty = self.cart[product_id]["quantity"]

            # Return quantity to stock
            fresh_product.stock += current_cart_qty
            fresh_product.save()

            # Remove from cart
            del self.cart[product_id]
            self.save()

    def get_cart_items(self):
        """
        Get all items in the cart with their details.
        """
        cart_items = []
        product_ids = self.cart.keys()

        # Get all products in cart in one query
        products = Product.objects.in_bulk(product_ids)

        for product_id, item_data in self.cart.items():
            if product_id in products:
                product = products[product_id]
                item_total = Decimal(item_data["price"]) * item_data["quantity"]

                cart_items.append(
                    {
                        "product": product,
                        "quantity": item_data["quantity"],
                        "price": Decimal(item_data["price"]),
                        "total": item_total,
                        "product_id": product_id,
                    }
                )

        return cart_items

    def get_total_price(self):
        """
        Calculate total price of all items in cart.
        """
        total = Decimal("0")
        for item_data in self.cart.values():
            total += Decimal(item_data["price"]) * item_data["quantity"]
        return total

    def get_total_quantity(self):
        """
        Get total number of items in cart.
        """
        return sum(item["quantity"] for item in self.cart.values())

    def get_item_total(self, product_id):
        """
        Get total price for a specific item in cart.
        """
        product_id = str(product_id)
        if product_id in self.cart:
            item = self.cart[product_id]
            return Decimal(item["price"]) * item["quantity"]
        return Decimal("0")

    def get_product_name(self, product_id):
        """
        Get product name from cart data.
        """
        product_id = str(product_id)
        if product_id in self.cart:
            return self.cart[product_id]["name"]
        return "Unknown Product"

    def clear(self):
        """
        Clear all items from cart and return their quantities to stock.
        """
        with transaction.atomic():
            # Return all quantities to stock before clearing
            for product_id, item_data in self.cart.items():
                fresh_product = Product.objects.select_for_update().get(id=product_id)
                fresh_product.stock += item_data["quantity"]
                fresh_product.save()

        del self.session[settings.CART_SESSION_ID]
        self.save()

    def save(self):
        """
        Mark session as modified to ensure it's saved.
        """
        self.session.modified = True
