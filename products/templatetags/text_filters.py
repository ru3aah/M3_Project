from django import template

register = template.Library()


@register.filter
def split_at_first_period(value, max_length=20):
    """
    Split text at the first period and return the first sentence.
    If no period is found, truncate at max_length.
    """
    if not value:
        return ""

    # Find the first period
    first_period = value.find(".")

    if first_period != -1:
        # Return text up to and including the first period
        return value[: first_period + 1]
    else:
        # If no period found, truncate at max_length
        if len(value) > max_length:
            return value[:max_length] + "..."
        return value
