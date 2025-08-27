from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.views import View
from products.models import Product
from cart.services import CartService
import json


class CartView(TemplateView):
    """
    View for displaying shopping cart items.
    Uses CartService to fetch and manage cart data.
    """

    template_name = "cart/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_service = CartService(self.request)
        context["cart_items"] = cart_service.get_cart_items()
        context["cart_total"] = cart_service.get_total_price()
        context["cart_count"] = cart_service.get_total_quantity()
        return context


@method_decorator(csrf_exempt, name="dispatch")
class AddToCartView(View):

    def post(self, request):
        try:
            data = json.loads(request.body)
            product_id = data.get("product_id")
            quantity = int(data.get("quantity", 1))

            if not product_id:
                return JsonResponse(
                    {"success": False, "error": "Product ID is required"}
                )

            product = get_object_or_404(Product, id=product_id, available=True)
            cart_service = CartService(request)

            # Check if we have enough stock
            if quantity > product.stock:
                return JsonResponse(
                    {
                        "success": False,
                        "error": f"Only {product.stock} items available in stock",
                    }
                )

            cart_service.add_to_cart(product, quantity)

            return JsonResponse(
                {
                    "success": True,
                    "message": f"{product.name} added to cart",
                    "cart_count": cart_service.get_total_quantity(),
                    "cart_total": str(cart_service.get_total_price()),
                }
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


@method_decorator(csrf_exempt, name="dispatch")
class UpdateCartView(View):

    def post(self, request):
        try:
            data = json.loads(request.body)
            product_id = data.get("product_id")
            quantity = int(data.get("quantity", 1))

            if not product_id:
                return JsonResponse(
                    {"success": False, "error": "Product ID is required"}
                )

            product = get_object_or_404(Product, id=product_id)
            cart_service = CartService(request)

            if quantity <= 0:
                cart_service.remove_from_cart(product_id)
                message = f"{product.name} removed from cart"
            else:
                # Check stock availability
                if quantity > product.stock:
                    return JsonResponse(
                        {
                            "success": False,
                            "error": f"Only {product.stock} items available in stock",
                        }
                    )

                cart_service.update_quantity(product_id, quantity)
                message = f"{product.name} quantity updated to {quantity}"

            return JsonResponse(
                {
                    "success": True,
                    "message": message,
                    "cart_count": cart_service.get_total_quantity(),
                    "cart_total": str(cart_service.get_total_price()),
                    "item_total": str(cart_service.get_item_total(product_id)),
                }
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


@method_decorator(csrf_exempt, name="dispatch")
class RemoveFromCartView(View):

    def post(self, request):
        try:
            data = json.loads(request.body)
            product_id = data.get("product_id")

            if not product_id:
                return JsonResponse(
                    {"success": False, "error": "Product ID is required"}
                )

            cart_service = CartService(request)
            product_name = cart_service.get_product_name(product_id)
            cart_service.remove_from_cart(product_id)

            return JsonResponse(
                {
                    "success": True,
                    "message": f"{product_name} removed from cart",
                    "cart_count": cart_service.get_total_quantity(),
                    "cart_total": str(cart_service.get_total_price()),
                }
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
