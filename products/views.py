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
    Handles the display of detailed information for a single product,
    including reviews and technical specifications.
    This view is tailored to aggregate and pre-process related objects
    to optimize database queries while providing a
    well-structured context for rendering the product details on a template.

    :ivar model: The model class associated with the view,
                representing the Product entity.
    :type model: Product
    :ivar queryset: The queryset used to fetch Product objects,
                    including category and prefetched related data
                    for reviews and tech specs.
    :type queryset: QuerySet[Product]
    :ivar template_name: The path to the template used to render the product details.
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


class ProductListView(ListView):
    """
    View for displaying a list of products with pagination, category filtering,
    search, and sorting features.

    :ivar model: The model associated with the view.
    :type model: Type[ModelBase]
    :ivar template_name: The template used to render the page.
    :type template_name: str
    :ivar paginate_by: Number of products to display per page.
    :type paginate_by: int
    :ivar allow_empty: Indicates whether an empty list is allowed.
    :type allow_empty: bool
    """

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
