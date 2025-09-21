from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """
    Divide una cadena por el argumento y devuelve la lista resultante.
    Ejemplo de uso: {{ value|split:":" }}
    """
    if value is None:
        return []
    return value.split(arg)

@register.filter
def format_price(value):
    """
    Formatea un número con puntos de mil.
    Ejemplo: 10000 -> 10.000
    """
    try:
        # Convertir a entero para eliminar decimales
        num = int(float(value))
        # Formatear con puntos de mil
        return "{:,}".format(num).replace(",", ".")
    except (ValueError, TypeError):
        return value