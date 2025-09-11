from django.urls import path

from resources.views import ResourcesView

app_name = "resources"

urlpatterns = [path("", ResourcesView.as_view(), name="resources")]
