from django.views.generic import CreateView, TemplateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy

from .forms import ShippingAddressForm
from .models import ShippingAddress
from users.forms import UserRegistrationForm


class UserCreateView(CreateView):
    form_class = UserRegistrationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")


class UserAccountView(TemplateView):
    template_name = "users/account.html"


class ShippingAddressCreateView(LoginRequiredMixin, CreateView):
    model = ShippingAddress
    form_class = ShippingAddressForm
    template_name = "users/address_form.html"
    login_url = "users:login"

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Make the newly added address default, replacing any previous one.
        with transaction.atomic():
            ShippingAddress.objects.filter(user=self.request.user, default=True).update(
                default=False
            )
            form.instance.default = True
            self.object = form.save()

        messages.success(self.request, "Shipping address saved and set as default.")
        return redirect(self.get_success_url())

    def get_success_url(self):
        # honor ?next=... if provided; otherwise go to checkout
        next_url = self.request.GET.get("next")
        return next_url or reverse_lazy("orders:checkout")
