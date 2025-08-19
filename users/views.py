from django.urls import reverse
from django.views.generic import CreateView
from users.forms import UserRegistrationForm


class UserCreateView(CreateView):
    form_class = UserRegistrationForm
    template_name = "users/register.html"
    success_url = "/"
