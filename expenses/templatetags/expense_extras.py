from django import template
from expenses.models import rupee as _rupee

register = template.Library()


@register.filter(name='rupee')
def rupee_filter(value):
    """Format a number as Indian rupees: whole numbers without decimals.

    Usage:  ₹{{ amount|rupee }}   ->   ₹6,000   or   ₹24.50
    """
    return _rupee(value)