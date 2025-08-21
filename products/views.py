from django.shortcuts import render
from django.views.generic import DetailView

from products.models import Product, ProductReview


class ProductDetailView(DetailView):
    model = Product
    queryset = Product.objects.all().select_related("category")
    template_name = "products/product_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reviews"] = ProductReview.objects.filter(product=self.object)
        return context
