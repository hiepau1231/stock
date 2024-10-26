from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='format_price')
def format_price(value):
    """Format a number as VND price"""
    try:
        value = float(value or 0)
        return f"{value:,.0f} VND"
    except (ValueError, TypeError):
        return "0 VND"

@register.filter(name='format_change')
def format_change(value):
    """Format price change with sign"""
    try:
        value = float(value)
        if value > 0:
            return f"+{value:,.0f}"
        return f"{value:,.0f}"
    except (ValueError, TypeError):
        return "0"

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
        value = float(value or 0)
        arg = float(arg or 0)
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

@register.filter(name='percentage')
def percentage(value):
    """Format số thành phần trăm với dấu +/-"""
    if value is None:
        return "N/A"
    try:
        value = float(value)
        sign = "+" if value > 0 else ""
        return f"{sign}{value:,.2f}%"
    except (ValueError, TypeError):
        return "0.00%"

@register.filter(name='percentage_of')
def percentage_of(value, total):
    """Tính phần trăm và format với dấu %"""
    try:
        if not total:
            return "0%"
        value = float(value)
        total = float(total)
        percentage = (value / total) * 100
        return f"{percentage:.1f}%"
    except (ValueError, TypeError, ZeroDivisionError):
        return "0%"

@register.filter(name='percentage_of_raw')
def percentage_of_raw(value, total):
    """Tính phần trăm và trả về số thập phân"""
    try:
        if not total:
            return 0
        value = float(value)
        total = float(total)
        return (value / total) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
