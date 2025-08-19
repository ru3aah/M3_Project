from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import User


class UserRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        )

        def clean_email(self):
            email = self.cleaned_data.get("email")
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Email already exists")
            return email

        def clean(self):
            cleaned_data = super().clean()
            password = cleaned_data.get("password1")
            confirm_password = cleaned_data.get("password2")
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match")
            return cleaned_data

        def save(self, commit=True):
            user = super().save(commit=False)
            user.set_password(self.cleaned_data["password1"])
            if commit:
                user.save()
            return user

        def __str__(self):
            return self.email
