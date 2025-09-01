from __future__ import annotations
from typing import Dict, Iterator, Any
from products.models import Product


class Cart:
    SESSION_KEY = "cart"

    def __init__(self, request):
        self.session = request.session
        self.cart: Dict[str, Dict[str, Any]] = self.session.get(self.SESSION_KEY, {})
        if any(isinstance(k, int) for k in self.cart.keys()):
            self.cart = {str(k): v for k, v in self.cart.items()}
        self._session_modified()

    def add(self, product_id: int) -> None:
        key = str(product_id)
        if key not in self.cart:
            product = Product.objects.get(id=product_id)
            self.cart[key] = {"quantity": 1, "price": str(product.price)}
            self._session_modified()

    def change_quantity(self, product_id: int, to_add: int) -> None:
        key = str(product_id)
        if key not in self.cart:
            self.add(product_id)
        old_q = int(self.cart[key]["quantity"])
        self.set_quantity(product_id, old_q + int(to_add))

    def set_quantity(self, product_id: int, quantity: int) -> None:
        print(self.cart)
        key = str(product_id)
        if key not in self.cart:
            self.add(product_id)
        if quantity <= 0:
            if key in self.cart:
                del self.cart[key]
        else:
            self.cart[key]["quantity"] = int(quantity)
        self._session_modified()

    def remove(self, product_id: int) -> None:
        key = str(product_id)
        if key in self.cart:
            del self.cart[key]
            self._session_modified()

    def clear(self) -> None:
        self.cart = {}
        self._session_modified()

    def get_quantity(self, product_id: int) -> int:
        key = str(product_id)
        data = self.cart.get(key)
        return int(data.get("quantity", 0)) if data else 0

    def __contains__(self, product_id: int) -> bool:
        return str(product_id) in self.cart

    def __len__(self) -> int:
        return sum(int(item["quantity"]) for item in self.cart.values())

    def __iter__(self) -> Iterator[dict]:
        product_ids = [int(pid) for pid in self.cart.keys()]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}
        for pid_str, data in self.cart.items():
            pid = int(pid_str)
            product = products.get(pid)
            if not product:
                continue
            yield {
                "product": product,
                "data": data,
                "total_price": float(data["quantity"]) * float(data["price"]),
            }

    def get_total_price(self) -> float:
        return sum(
            float(item["quantity"]) * float(item["price"])
            for item in self.cart.values()
        )

    # internal
    def _session_modified(self) -> None:
        self.session[self.SESSION_KEY] = self.cart
        self.session.modified = True
