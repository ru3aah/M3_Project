from tokenize import endpats

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
        self.change_qty(product_id, self.cart[product_id]["quantity"] + qty_diff)

    def remove(self, product_id: int, qty_diff: int = -1):
        if product_id in self.cart:
            self.change_qty(product_id, self.cart[product_id]["quantity"] + qty_diff)

    def change_qty(self, product_id: int, new_qty: int):
        product = Product.objects.get(id=product_id)
        if product_id in self.cart:
            qty_diff = new_qty - self.cart[product_id]["quantity"]
            if qty_diff > product.stock:
                self.cart[product_id]["quantity"] = (
                    self.cart[product_id]["quantity"] + product.stock
                )
                product.stock = 0
            else:
                if new_qty <= 0:
                    product.stock = product.stock + self.cart[product_id]["quantity"]
                    del self.cart[product_id]
                else:
                    self.cart[product_id]["quantity"] = new_qty
                    product.stock = product.stock - qty_diff
            self.save()

    def clear(self):
        self.session.pop(self.SESSION_KEY)

    def save(self):
        self.session.modified = True

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
