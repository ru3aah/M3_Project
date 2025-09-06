from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
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
            success_url="account/",
        ),
        name="login",
    ),
    path("account/", views.UserAccountView.as_view(), name="account"),
    path(
        "logout/", LogoutView.as_view(next_page="products:product-list"), name="logout"
    ),
    path("addresses/add/", ShippingAddressCreateView.as_view(), name="address_add"),
]
