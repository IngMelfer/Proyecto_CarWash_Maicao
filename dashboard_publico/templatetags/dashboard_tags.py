from django import template

register = template.Library()

@register.simple_tag
def is_public_dashboard(request):
    return request.path == '/dashboard-publico/'