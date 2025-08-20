from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView
from users.forms import UserRegistrationForm, UserLoginForm


class UserCreateView(CreateView):
    form_class = UserRegistrationForm
    template_name = "users/register.html"
    get_success_url = reverse_lazy("users:login")


class UserLoginView(LoginView):
    template_name = "users/login.html"
    form_class = UserLoginForm

    redirect_authenticated_user = True

    def get_success_url(self):
        return "/"
