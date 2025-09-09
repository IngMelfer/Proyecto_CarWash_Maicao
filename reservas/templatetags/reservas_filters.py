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