from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.urls import reverse_lazy  # <-- add this
from users import views
from users.forms import UserLoginForm
from users.views import ShippingAddressCreateView

app_name = "users"

urlpatterns = [
    path("register/", views.UserCreateView.as_view(), name="register"),
    path(
        "login/",
        LoginView.as_view(
            template_name="users/login.html",
            authentication_form=UserLoginForm,
            redirect_authenticated_user=True,
            success_url=reverse_lazy("users:account"),
        ),
        name="login",
    ),
    path("account/", views.account_view, name="account"),
    path(
        "logout/",
        LogoutView.as_view(
            next_page=reverse_lazy("products:product-list")
        ),  # <-- fixed
        name="logout",
    ),
    path("addresses/add/", ShippingAddressCreateView.as_view(), name="address_add"),
    path("addresses/<int:pk>/update/", views.address_update, name="address_update"),
    path("addresses/<int:pk>/delete/", views.address_delete, name="address_delete"),
]
