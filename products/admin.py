from django.contrib import admin

from .models import Product, Category, ProductReview


class ProductAdmin(admin.ModelAdmin):
    """
    The ProductAdmin class is used to define the administrative interface
    for the Product model. This class customizes the display, filtering,
    searching, and prepopulation functionalities in the Django admin panel
    to enhance usability and maintain consistency in the administration of
    Product entities.

    :ivar list_display: Fields of the Product model to display in the admin
        interface list view.
    :type list_display: tuple
    :ivar prepopulated_fields: Fields of the Product model that should be
        automatically populated based on the value of other fields.
    :type prepopulated_fields: dict
    :ivar search_fields: Fields of the Product model that are searchable
        in the admin interface.
    :type search_fields: tuple
    :ivar list_filter: Fields of the Product model to use for filtering
        results in the admin interface.
    :type list_filter: tuple
    """

    list_display = (
        "category",
        "name",
        "slug",
        "image",
        "price",
        "currency",
        "unit_measure",
        "stock",
        "description",
        "available",
    )
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    list_filter = ("available",)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent")
    list_display_links = ("name", "parent")

    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    list_filter = ("parent",)


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductReview)
