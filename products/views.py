from django.views.generic import DetailView, ListView, TemplateView

from products.models import Product, ProductReview, Category
from django.db import models


class ProductDetailView(DetailView):
    """
    Handles the display of detailed information for a specific product.

    This view is responsible for rendering the details of a single
    `Product` instance. It uses the specified queryset to optimize
    database access by selecting related data for the `category` field
    and prefetching recent `reviews` for the product. The template
    used for rendering is defined in the `template_name` attribute.

    :ivar model: The model associated with this DetailView.
    :type model: Product
    :ivar queryset: Queryset to fetch the product instance along with
         a related category and prefetch recent reviews.
    :type queryset: QuerySet
    :ivar template_name: Path to the template used for rendering the
        product details.
    :type template_name: str
    """

    model = Product
    queryset = (
        Product.objects.all()
        .select_related("category")
        .prefetch_related(
            models.Prefetch(
                "reviews",
                queryset=ProductReview.objects.order_by("-created_at"),
                to_attr="recent_reviews",
            )
        )
    )
    template_name = "products/product_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reviews"] = self.object.recent_reviews[:3]
        return context


class ProductListView(ListView):
    model = Product
    queryset = Product.objects.filter(available=True)

    template_name = "products/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["products"] = self.get_queryset()
        return context


class GuidesRecipesView(TemplateView):
    template_name = "guides-recipes.html"
