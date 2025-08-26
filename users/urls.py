from django.contrib.auth.views import LoginView
from django.urls import path
from users import views
from users.forms import UserLoginForm

app_name = "users"

urlpatterns = [
    path("register/", views.UserCreateView.as_view(), name="register"),
    path(
        "login/",
        LoginView.as_view(
            template_name="users/login.html",
            authentication_form=UserLoginForm,
            redirect_authenticated_user=True,
            success_url="/",
        ),
        name="login",
    ),
    path("account/", views.UserAccountView.as_view(), name="account"),
]
