from django.urls import reverse
from django.views.generic import CreateView, FormView
from users.forms import UserRegistrationForm


class UserCreateView(CreateView):
    form_class = UserRegistrationForm
    template_name = "users/register.html"
    success_url = "/"


class UserLoginView(FormView):
    form_class = UserRegistrationForm
    template_name = "users/login.html"
