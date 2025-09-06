from django import forms
from users.models import ShippingAddress


class CheckoutForm(forms.Form):
    full_name = forms.CharField(label="Full Name", max_length=150, required=True)
    phone = forms.CharField(label="Phone Number", max_length=50, required=True)
    city = forms.CharField(label="City", max_length=100, required=True)

    # CHANGED: was CharField textarea; now selects from user's saved addresses
    shipping_address = forms.ModelChoiceField(
        label="Shipping Address",
        queryset=ShippingAddress.objects.none(),
        required=True,
        empty_label=None,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # style widgets
        self.fields["full_name"].widget.attrs.update(
            {"id": "full-name", "class": "Input", "placeholder": "Your full name"}
        )
        self.fields["phone"].widget.attrs.update(
            {"id": "phone", "class": "Input", "placeholder": "+123 456 789"}
        )
        self.fields["city"].widget.attrs.update(
            {"id": "city", "class": "Input", "placeholder": "City"}
        )

        # keep same id/class as you had for the textarea for drop-in styling
        self.fields["shipping_address"].widget.attrs.update(
            {"id": "address", "class": "Input"}
        )

        # Pre-populate from user
        if user:
            # addresses for the select (default first if present)
            qs = user.shipping_addresses.all().order_by("-default", "id")
            self.fields["shipping_address"].queryset = qs

            default_addr = qs.filter(default=True).first()
            if default_addr and not self.is_bound:
                self.initial.setdefault("shipping_address", default_addr.pk)

            # Derive full name + phone
            if not self.is_bound:
                fn = (getattr(user, "first_name", "") or "").strip()
                ln = (getattr(user, "last_name", "") or "").strip()
                if fn or ln:
                    self.initial.setdefault("full_name", f"{fn} {ln}".strip())
                phone = (getattr(user, "phone", "") or "").strip()
                if phone:
                    self.initial.setdefault("phone", phone)
