from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='format_price')
def format_price(value):
    """Format a number as VND price"""
    if value is None:
        return "N/A"
    try:
        value = float(value)
        formatted = "{:,.0f}".format(value)
        formatted = formatted.replace(',', '.')
        return f"{formatted} VND"
    except (ValueError, TypeError):
        return value

@register.filter(name='format_change')
def format_change(value):
    """Format price change with sign"""
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
    """Format percentage with sign"""
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
    """Format volume with dots as thousand separators"""
    if value is None:
        return "N/A"
    try:
        value = int(value)
        return "{:,.0f}".format(value).replace(',', '.')
    except (ValueError, TypeError):
        return value

@register.filter(name='subtract')
def subtract(value, arg):
    """Subtract two numbers"""
    try:
        if isinstance(value, str):
            value = float(value.replace(',', '').replace('.', '').replace('VND', '').strip())
        if isinstance(arg, str):
            arg = float(arg.replace(',', '').replace('.', '').replace('VND', '').strip())
        return value - arg
    except (ValueError, TypeError):
        return 0

@register.filter(name='calculate_change')
def calculate_change(close_price, open_price):
    """Calculate price change and format it"""
    try:
        change = float(close_price) - float(open_price)
        return format_change(change)
    except (ValueError, TypeError):
        return "N/A"
