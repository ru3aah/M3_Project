from django import template

register = template.Library()


@register.simple_tag
def cart_quantity(cart, product):
    pid = getattr(product, "id", product)
    return cart.get_quantity(pid)


@register.filter
def in_cart(cart, product):
    pid = getattr(product, "id", product)
    return pid in cart
