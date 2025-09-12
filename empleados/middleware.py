from django.urls import resolve
from django.http import HttpResponseForbidden
from django.contrib import admin
from autenticacion.models import Usuario

class AdminAccessMiddleware:
    """
    Middleware para controlar el acceso a las vistas de administración de TipoDocumento y Cargo.
    Solo permite el acceso al administrador del sistema.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Procesar la solicitud solo si es una vista de administración
        if request.path.startswith('/admin/'):
            # Verificar si el usuario está autenticado
            if not request.user.is_authenticated:
                return self.get_response(request)
            
            # Obtener la URL actual
            current_url = resolve(request.path)
            
            # Verificar si es una vista de administración de TipoDocumento o Cargo
            if 'tipodocumento' in request.path or 'cargo' in request.path:
                # Verificar si el usuario es administrador del sistema
                if not (request.user.is_superuser or 
                        (hasattr(request.user, 'rol') and 
                         request.user.rol == Usuario.ROL_ADMIN_SISTEMA)):
                    return HttpResponseForbidden("No tienes permisos para acceder a esta página.")
        
        # Continuar con la solicitud
        return self.get_response(request)