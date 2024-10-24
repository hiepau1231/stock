from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='format_price')
def format_price(value):
    """
    Format a number as VND price
    Example: 1234567 -> 1.234.567 VND
    """
    if value is None:
        return "N/A"
    
    try:
        value = float(value)
        formatted = "{:,.0f}".format(value)
        # Thay dấu phẩy bằng dấu chấm
        formatted = formatted.replace(',', '.')
        return f"{formatted} VND"
    except (ValueError, TypeError):
        return value

@register.filter(name='format_change')
def format_change(value):
    """
    Format price change with sign
    Example: 1234.56 -> +1.234,56 VND
    """
    if value is None:
        return "N/A"
    
    try:
        value = float(value)
        sign = "+" if value > 0 else ""
        formatted = "{:,.0f}".format(abs(value))
        formatted = formatted.replace(',', '.')
        return f"{sign}{formatted} VND" if value != 0 else "0 VND"
    except (ValueError, TypeError):
        return value

@register.filter(name='format_percent')
def format_percent(value):
    """
    Format percentage with sign
    Example: 12.34 -> +12,34%
    """
    if value is None:
        return "N/A"
    
    try:
        value = float(value)
        sign = "+" if value > 0 else ""
        return f"{sign}{value:,.2f}%"
    except (ValueError, TypeError):
        return value

@register.filter(name='format_volume')
def format_volume(value):
    """
    Format volume with dots as thousand separators
    Example: 1234567 -> 1.234.567
    """
    if value is None:
        return "N/A"
    
    try:
        value = int(value)
        return "{:,.0f}".format(value).replace(',', '.')
    except (ValueError, TypeError):
        return value
