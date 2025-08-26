from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf.urls.static import static
from config.settings import DEBUG, MEDIA_URL, MEDIA_ROOT


def home_redirect(request):
    return redirect("products:product-list")


urlpatterns = [
    path("", home_redirect),
    path("admin/", admin.site.urls),
    path("users/", include("users.urls", namespace="users")),
    path("products/", include("products.urls", namespace="products")),
    path("resources/", include("resources.urls", namespace="resources")),
    path("community/", include("community.urls", namespace="community")),
    path("contacts/", include("contacts.urls", namespace="contacts")),
]

# Serve media files during development
if DEBUG:
    import debug_toolbar

    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
