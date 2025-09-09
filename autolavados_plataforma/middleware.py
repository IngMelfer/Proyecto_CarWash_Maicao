from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
import re
import logging
import traceback
import sys

logger = logging.getLogger(__name__)

class CSRFDebugMiddleware(MiddlewareMixin):
    """Middleware para diagnosticar problemas con CSRF"""
    
    def process_request(self, request):
        # Registrar información sobre cookies y tokens CSRF
        logger.debug(f"CSRF Cookie: {request.COOKIES.get('csrftoken')}, CSRF Token: {request.META.get('CSRF_COOKIE')}")
        return None
    
    def process_response(self, request, response):
        # Asegurar que la cookie CSRF esté configurada correctamente
        if 'csrftoken' not in request.COOKIES and 'Set-Cookie' in response:
            logger.debug(f"Setting CSRF cookie in response: {response['Set-Cookie']}")
        return response


class AJAXExceptionMiddleware:
    """Middleware para manejar excepciones en solicitudes AJAX y devolver respuestas JSON"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Solo manejar excepciones para solicitudes AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Registrar el error para depuración
                logger.error(f"Error en solicitud AJAX: {str(e)}\n{traceback.format_exc()}")
                
                # Devolver respuesta JSON con el error
                return JsonResponse({
                    'success': False,
                    'error': f'Error interno del servidor: {str(e)}'
                }, status=500)
            # Para solicitudes normales, dejar que Django maneje la excepción
            raise


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
            r'^/admin/.*$',  # Permitir acceso a todo el panel de administración
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
                    return JsonResponse({'detail': 'Authentication required'}, status=401)
                # De lo contrario, redirigir al login
                return redirect(settings.LOGIN_URL)
        
        response = self.get_response(request)
        return response