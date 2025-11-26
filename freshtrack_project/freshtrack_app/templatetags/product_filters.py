from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def expiry_timestamp(product):
    """Convert expiry datetime to JavaScript timestamp in milliseconds"""
    if product.expiry_datetime:
        return int(product.expiry_datetime.timestamp() * 1000)
    return 0
