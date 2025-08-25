from django.views.generic import DetailView, ListView, TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    paginate_by = 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        # Remove the products line as page_obj already contains paginated products
        return context

    def paginate_queryset(self, queryset, page_size):
        """Override to handle pagination errors gracefully"""
        paginator = self.get_paginator(
            queryset,
            page_size,
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
        )

        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1

        try:
            page_number = int(page)
        except ValueError:
            page_number = 1

        # Ensure page number is at least 1
        if page_number < 1:
            page_number = 1

        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except (EmptyPage, PageNotAnInteger):
            # If page is out of range or not an integer, deliver first page
            page = paginator.page(1)
            return (paginator, page, page.object_list, page.has_other_pages())


class GuidesRecipesView(TemplateView):
    template_name = "guides-recipes.html"
