from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = (
        "id",
        "user",
        "status",
        "payment_method",
        "total_price",
        "created_at",
        "updated_at",
    )
    list_display_links = ("id", "user")
    list_filter = ("status", "payment_method", "created_at", "updated_at")
    search_fields = (
        "id",
        "user__first_name",
        "user__last_name",
        "user__username",
        "user__email",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "price", "quantity")
    list_display_links = ("id", "order")
    list_filter = ("order", "product")
    search_fields = (
        "order__id",
        "order__user__first_name",
        "order__user__last_name",
        "order__user__username",
        "order__user__email",
        "product__name",
    )
    # OrderItem has no created_at field; if you want newest first,
    # sort by the parent Order's created_at or simply by id:
    ordering = ("-order__created_at",)  # or: ordering = ("-id",)
