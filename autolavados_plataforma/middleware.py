from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.middleware.csrf import get_token
import re
import logging
import traceback
import sys

logger = logging.getLogger(__name__)

class CSRFDebugMiddleware:
    """Middleware para diagnosticar problemas con CSRF"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Verificar que estamos trabajando con un objeto request válido
        # y no con una instancia de View u otro objeto
        if not isinstance(request, type) and hasattr(request, '__class__'):
            try:
                # Verificar si hay cookie CSRF solo si el request tiene los atributos necesarios
                if hasattr(request, 'COOKIES') and hasattr(request, 'META') and hasattr(request, 'path'):
                    # Verificar si hay cookie CSRF
                    csrf_cookie = request.COOKIES.get('csrftoken')
                    csrf_token = request.META.get('CSRF_COOKIE')
                    
                    # Registrar información sobre cookies y tokens CSRF
                    logger.debug(f"CSRF Cookie: {csrf_cookie}")
                    logger.debug(f"CSRF Token: {csrf_token}")
                    logger.debug(f"Request Path: {request.path}")
                    
                    # Asegurar que la cookie CSRF esté configurada para todas las solicitudes
                    if not csrf_cookie and '/autenticacion/login/' not in request.path:
                        # Forzar la configuración de la cookie CSRF excepto para la página de login
                        get_token(request)
                        logger.debug("CSRF token generado forzosamente")
            except Exception as e:
                logger.error(f"Error en CSRFDebugMiddleware: {str(e)}")
        else:
            logger.warning(f"Objeto no es un request válido para CSRF: {type(request).__name__ if hasattr(request, '__name__') else str(type(request))}")
        
        response = self.get_response(request)
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
            r'^/media/.*$',  # Permitir acceso a archivos media
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