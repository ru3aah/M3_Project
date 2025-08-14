from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.views.generic import CreateView


class UserCreateView(CreateView):
    form_class = UserCreationForm
