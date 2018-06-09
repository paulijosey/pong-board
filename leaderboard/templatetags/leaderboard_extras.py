from django import template

register = template.Library()


@register.filter
def percentage(value, decimal_places=0):
    """Convert number to percentage with specified decimal places."""
    percentage = format(value, f'.{decimal_places}%')
    return percentage
