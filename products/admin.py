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
    """
    Represents the administrative interface for managing Category objects.

    This class customizes the display and behavior of the Category model within
    the Django admin site. It defines how fields are displayed, searchable,
    and filtered in the admin interface. The class is used to provide a
    more user-friendly and efficient way to manage Category data.

    :ivar list_display: Specifies the fields displayed in the admin list view.
    :type list_display: tuple
    :ivar list_display_links: Specifies which fields in the admin list view are clickable
                              to edit the corresponding record.
    :type list_display_links: tuple
    :ivar prepopulated_fields: Specifies fields that will be automatically populated
                               based on the values of other fields.
    :type prepopulated_fields: dict
    :ivar search_fields: Specifies the fields that can be searched within the admin
                         interface.
    :type search_fields: tuple
    :ivar list_filter: Specifies the fields used to filter results in the admin list view.
    :type list_filter: tuple
    """

    list_display = ("name", "slug", "parent")
    list_display_links = ("name", "parent")

    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    list_filter = ("parent",)


class ProductReviewAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "user",
        "title",
        "comment",
        "rating",
        "created_at",
        "updated_at",
    )
    list_filter = ("product", "user")
    search_fields = ("product", "user", "title", "comment")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
