from django.urls import path

from contacts.views import ContactsView
from users.urls import app_name

app_name = "contacts"

urlpatterns = [
    path("", ContactsView.as_view(), name="contacts"),
]
