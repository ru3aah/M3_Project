from django.contrib import admin
from .models import Product, Category, ProductReview, ProductTechSpec
from .admin_forms import ProductTechSpecJSONForm


class ProductTechSpecInline(admin.TabularInline):
    """
    Inline that shows (Name, Value) instead of the raw JSON field.
    """

    model = ProductTechSpec
    form = ProductTechSpecJSONForm
    fields = ("spec_name", "spec_value")
    extra = 1
    can_delete = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "category",
        "image",
        "price",
        "currency",
        "unit_measure",
        "stock",
        "description",
        "available",
        "tech_specs_count",
    )
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    list_filter = ("available",)
    inlines = [ProductTechSpecInline]

    def tech_specs_count(self, obj):
        return obj.tech_specs.count()

    tech_specs_count.short_description = "Tech Specs"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent")
    list_display_links = ("name", "parent")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    list_filter = ("parent",)


@admin.register(ProductReview)
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
    list_display_links = ("product", "user")
    list_filter = ("product", "user")
    search_fields = ("product", "user", "title", "comment", "rating")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25


@admin.register(ProductTechSpec)
class ProductTechSpecAdmin(admin.ModelAdmin):
    list_display = ("product", "tech_spec")
