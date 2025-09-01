from django import template

register = template.Library()


@register.filter(name="range")
def template_range(stop, start=0):
    return range(start, stop)


@register.simple_tag()
def update_query_string(request, value, key="page"):
    params = request.GET.copy()
    params[key] = value
    return params.urlencode()
