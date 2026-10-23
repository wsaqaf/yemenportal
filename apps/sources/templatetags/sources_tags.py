from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    if not dictionary:
        return None
    return dictionary.get(key)
