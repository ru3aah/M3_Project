from django.views.generic import TemplateView


class CommunityView(TemplateView):
    template_name = "community/community.html"
