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

        # Update widget attributes for styling and accessibility
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

        # Pre-populate form fields with user data if available
        if user and not self.is_bound:
            # Handle full name creation from user's first and last name
            fn = getattr(user, "first_name", "") or ""
            ln = getattr(user, "last_name", "") or ""

            if fn or ln:  # Only create full_name if we have at least one name
                full_name = f"{fn.strip()} {ln.strip()}".strip()
                self.initial.setdefault("full_name", full_name)

            # Handle phone number with validation
            phone = getattr(user, "phone", None)
            if phone:
                phone = str(phone).strip()
                if phone:  # Ensure it's not just whitespace
                    self.initial.setdefault("phone", phone)
