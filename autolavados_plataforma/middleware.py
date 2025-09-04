from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve
import re

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs que no requieren autenticación (usando expresiones regulares)
        self.exempt_urls = [
            r'^/autenticacion/login/$',
            r'^/autenticacion/registro/$',
            r'^/autenticacion/verificar-email/.*$',
            r'^/autenticacion/recuperar-password/$',
            r'^/autenticacion/reset-password/.*$',
            r'^/autenticacion/api/login/$',
            r'^/autenticacion/api/registro/$',
            r'^/admin/login/$',
            r'^/static/.*$',  # Permitir acceso a archivos estáticos
        ]
        self.exempt_url_patterns = [re.compile(url) for url in self.exempt_urls]

    def __call__(self, request):
        # Si el usuario no está autenticado y la URL no está exenta
        if not request.user.is_authenticated:
            path = request.path_info
            
            # Verificar si la URL actual está en la lista de exentas
            if not any(pattern.match(path) for pattern in self.exempt_url_patterns):
                # Si es una solicitud AJAX o API, devolver 401
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or path.startswith('/api/'):
                    from django.http import JsonResponse
                    return JsonResponse({'detail': 'Authentication required'}, status=401)
                # De lo contrario, redirigir al login
                return redirect(settings.LOGIN_URL)
        
        response = self.get_response(request)
        return response