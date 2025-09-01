from products.models import Product


class Cart:
    SESSION_KEY = "cart"
    # {'product_id': {'quantity': 1, 'price': 100}}

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(self.SESSION_KEY, {})
        if not cart:
            cart = self.session[self.SESSION_KEY] = {}
        self.cart = cart

    def add(self, product_id: int, qty_diff: int = 1):
        product = Product.objects.get(id=product_id)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0, "price": product.price}

    def remove(self, product_id: int, qty_diff: int = -1):
        pass

    def clear(self):
        pass

    def change_qty(self, product_id: int, new_qty: int):
        pass

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
