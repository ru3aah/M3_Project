from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from users.forms import UserRegistrationForm


class UserCreateView(CreateView):
    form_class = UserRegistrationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")


class UserAccountView(TemplateView):
    template_name = "users/account.html"


class UserCommunityView(TemplateView):
    template_name = "community.html"
