from django.contrib.auth.views import LoginView
from django.urls import path

from users import views
from users.forms import UserLoginForm

app_name = "users"

urlpatterns = [
    path("register/", views.UserCreateView.as_view(), name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
]
