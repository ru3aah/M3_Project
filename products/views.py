from django.shortcuts import render
from django.views.generic import DetailView

from products.models import Product


class ProductDetailView(DetailView):
    model = Product
    queryset = Product.objects.all().select_related("category")
    template_name = "products/product_details.html"
