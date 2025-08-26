from django.urls import path

from community.views import CommunityView
from users.urls import app_name

app_name = "community"

urlpatterns = [
    path("", CommunityView.as_view(), name="community"),
]
