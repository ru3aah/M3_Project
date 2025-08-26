from tokenize import endpats
from unicodedata import category

from django.db.models import Q
from django.views.generic import DetailView, ListView, TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from config.settings import PRODUCTS_QUERY_MAP
from products.models import Product, ProductReview, Category, ProductTechSpec
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
            ),
            models.Prefetch(
                "tech_specs",
                queryset=ProductTechSpec.objects.all(),
                to_attr="product_tech_specs",
            ),
        )
    )
    template_name = "products/product_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reviews"] = self.object.recent_reviews[:3]

        # Process tech specs to handle different value types properly
        processed_specs = []
        for spec in self.object.product_tech_specs:
            if (
                spec.tech_spec
                and "name" in spec.tech_spec
                and "value" in spec.tech_spec
            ):
                spec_name = spec.tech_spec.get("name", "")
                spec_value = spec.tech_spec.get("value", "")

                if spec_name and spec_value:
                    # Handle different value types
                    if isinstance(spec_value, list):
                        # If it's a list, join the items
                        if all(
                            isinstance(item, dict)
                            and "name" in item
                            and "value" in item
                            for item in spec_value
                        ):
                            # List of objects with name/value pairs
                            formatted_value = ", ".join(
                                [
                                    f"{item['name']}: {item['value']}"
                                    for item in spec_value
                                ]
                            )
                        else:
                            # List of simple values
                            formatted_value = ", ".join(
                                [str(item) for item in spec_value]
                            )
                    else:
                        # It's a string or other simple value
                        formatted_value = str(spec_value)

                    processed_specs.append(
                        {"name": spec_name, "value": formatted_value}
                    )

        context["tech_specs"] = processed_specs
        return context


class Pruduct:
    pass


class ProductListView(ListView):
    model = Product
    template_name = "products/home.html"
    paginate_by = 12
    allow_empty = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["tech_specs"] = ProductTechSpec.objects.all()
        return context

    def get_queryset(self):
        qs = (
            Product.objects.filter(available=True)
            .select_related("category")
            .annotate(rating=models.Avg("reviews__rating"))
        )
        # filter by category
        categories = self.request.GET.get("categories", None)
        if categories:
            qs = qs.filter(category__slug__in=categories.split(","))

        # search
        to_search = self.request.GET.get("q", None)
        if to_search:
            qs = qs.filter(Q(name__icontains=to_search))

        # sort
        qs_key = self.request.GET.get("sort", "new")
        qs = qs.order_by(PRODUCTS_QUERY_MAP[qs_key])

        return qs

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
        except (ValueError, TypeError):
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
