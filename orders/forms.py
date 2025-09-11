from django import forms
from users.models import ShippingAddress


class CheckoutForm(forms.Form):
    full_name = forms.CharField(label="Full Name", max_length=150, required=True)
    phone = forms.CharField(label="Phone Number", max_length=50, required=True)
    shipping_address = forms.ModelChoiceField(
        label="Shipping Address",
        queryset=ShippingAddress.objects.none(),
        required=False,  # stays valid when the user has no addresses
        empty_label=None,
        widget=forms.Select(attrs={"id": "address", "class": "Input"}),
    )

    @staticmethod
    def _addr_label(addr: ShippingAddress) -> str:
        parts = [addr.address_line_1]
        if addr.address_line_2:
            parts.append(addr.address_line_2)
        tail = f"{addr.postal_code} {addr.city}, {addr.country}".strip()
        return f"{', '.join(parts)} — {tail}"

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["full_name"].widget.attrs.update(
            {"id": "full-name", "class": "Input", "placeholder": "Your full name"}
        )
        self.fields["phone"].widget.attrs.update(
            {"id": "phone", "class": "Input", "placeholder": "+123 456 789"}
        )

        if user and not self.is_bound:
            fn = (getattr(user, "first_name", "") or "").strip()
            ln = (getattr(user, "last_name", "") or "").strip()
            if fn or ln:
                self.initial.setdefault("full_name", f"{fn} {ln}".strip())
            phone = getattr(user, "phone", None)
            if phone:
                phone = str(phone).strip()
                if phone:
                    self.initial.setdefault("phone", phone)

        # Set address queryset for the current user
        addresses = ShippingAddress.objects.none()
        if user:
            addresses = ShippingAddress.objects.filter(user=user).order_by(
                "-default", "-id"
            )

        field = self.fields["shipping_address"]
        field.queryset = addresses

        field.label_from_instance = self._addr_label

        if not addresses.exists():
            field.required = False
            field.widget.attrs["disabled"] = "disabled"
            field.choices = [("", "No any address available")]
