from django import template
from urllib.parse import urlencode

register = template.Library()


@register.filter
def get_item(d, key):
    """Dict get in templates."""
    if not isinstance(d, dict):
        return None
    return d.get(key)


@register.simple_tag
def querystring(params, key, value):
    """
    Build a querystring from a QueryDict (request.GET) replacing a single key.
    Usage: ?{% querystring request.GET 'page' 2 %}
    Preserves all existing filters.
    """
    if hasattr(params, "copy"):
        qd = params.copy()
    else:
        # Fallback if someone passes a plain dict
        from django.http import QueryDict

        qd = QueryDict(mutable=True)
        for k, v in (params or {}).items():
            qd.setlist(k, v if isinstance(v, list) else [v])

    qd[key] = str(value)
    return urlencode([(k, v) for k in qd for v in qd.getlist(k)])
