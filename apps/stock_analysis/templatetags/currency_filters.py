from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='format_vnd')
def format_vnd(value):
    """
    Format a number as VND currency
    Example: 1234567.89 -> 1.234.567,89 ₫
    """
    if value is None:
        return "N/A"
    
    try:
        value = float(value)
        # Làm tròn đến 2 chữ số thập phân
        formatted = "{:,.2f}".format(value)
        # Thay dấu phẩy bằng dấu chấm cho hàng nghìn và dấu chấm bằng dấu phẩy cho phần thập phân
        formatted = formatted.replace(",", "@").replace(".", ".").replace("@", ".")
        return f"{formatted} ₫"
    except (ValueError, TypeError):
        return value

@register.filter(name='format_change')
def format_change(value):
    """
    Format change value with + or - sign
    Example: 1234.56 -> +1.234,56 ₫
    """
    if value is None:
        return "N/A"
    
    try:
        value = float(value)
        sign = "+" if value > 0 else ""
        formatted = "{:,.2f}".format(value)
        formatted = formatted.replace(",", "@").replace(".", ".").replace("@", ".")
        return f"{sign}{formatted} ₫"
    except (ValueError, TypeError):
        return value
