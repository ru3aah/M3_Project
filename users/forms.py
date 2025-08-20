from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import User


class UserRegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "placeholder": "Password",
                "class": "Input",
            }
        ),
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "placeholder": "Password again",
                "class": "Input",
            }
        ),
        strip=False,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "placeholder": "Your username",
                    "class": "Input",
                },
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "your@mail.com", "class": "Input"}
            ),
            "first_name": forms.TextInput(
                attrs={"placeholder": "John", "class": "Input"}
            ),
            "last_name": forms.TextInput(
                attrs={"placeholder": "Doe", "class": "Input"}
            ),
        }

        labels = {
            "username": "Username",
            "email": "e-mail",
            "first_name": "First name",
            "last_name": "Family name",
            "password1": "Password",
            "password2": "Confirm password",
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email
