from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, TemplateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from orders.models import OrderStatus, Order
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


@login_required(login_url="users:login")
def account_view(request):
    user = request.user

    if request.method == "POST":
        first_name = (request.POST.get("first_name") or "").strip()
        last_name = (request.POST.get("last_name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        phone = (request.POST.get("phone") or "").strip()
        username = (request.POST.get("username") or "").strip()
        image = request.FILES.get("image")

        errors = []
        changed = False

        if first_name != user.first_name:
            user.first_name = first_name
            changed = True
        if last_name != user.last_name:
            user.last_name = last_name
            changed = True

        if email and email != user.email:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            if User.objects.filter(email=email).exclude(pk=user.pk).exists():
                errors.append("This email is already taken.")
            else:
                user.email = email
                changed = True

        if username and username != user.username:
            if User.objects.filter(username=username).exclude(pk=user.pk).exists():
                errors.append("This username is already taken.")
            else:
                user.username = username
                changed = True

        if phone != (user.phone or ""):
            user.phone = phone
            changed = True

        if image:
            user.image = image
            changed = True

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            if changed:
                user.save()
                messages.success(request, "Your profile has been updated.")
            else:
                messages.info(request, "No changes to save.")

    addresses = ShippingAddress.objects.filter(user=user).order_by("-default", "id")
    orders = (
        Order.objects.filter(user=user)
        .select_related("shipping_address")
        .order_by("status", "-created_at")
    )

    return render(
        request,
        "users/user_account.html",
        {
            "user_obj": user,
            "addresses": addresses,
            "orders": orders,
            "OrderStatus": OrderStatus,
        },
    )
