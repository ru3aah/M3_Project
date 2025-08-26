from django.views.generic import TemplateView


class ResourcesView(TemplateView):
    template_name = "resources/resources.html"
