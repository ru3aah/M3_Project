from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(label="Full Name", max_length=150, required=True)
    phone = forms.CharField(label="Phone Number", max_length=50, required=True)
    city = forms.CharField(label="City", max_length=100, required=True)
    shipping_address = forms.CharField(
        label="Shipping Address",
        max_length=500,
        required=True,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["full_name"].widget.attrs.update(
            {"id": "full-name", "class": "Input", "placeholder": "Your full name"}
        )
        self.fields["phone"].widget.attrs.update(
            {"id": "phone", "class": "Input", "placeholder": "+123 456 789"}
        )
        self.fields["city"].widget.attrs.update(
            {"id": "city", "class": "Input", "placeholder": "City"}
        )
        self.fields["shipping_address"].widget.attrs.update(
            {
                "id": "address",
                "class": "Textarea",
                "placeholder": "Street, ZIP, Country",
            }
        )

        if user and not self.is_bound:
            fn = (user.first_name or "").strip()
            ln = (user.last_name or "").strip()
            full_name = f"{fn} {ln}".strip()
            phone = (getattr(user, "phone", "") or "").strip()

            if full_name:
                self.initial.setdefault("full_name", full_name)
            if phone:
                self.initial.setdefault("phone", phone)
