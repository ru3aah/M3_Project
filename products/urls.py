from django.urls import path

from .views import ProductDetailView, ProductListView, GuidesRecipesView

app_name = "products"

urlpatterns = [
    path("home/", ProductListView.as_view(), name="product-list"),
    path("guides/", GuidesRecipesView.as_view(), name="guides-recipes"),
    path("<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
]
