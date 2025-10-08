from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse


def empleado_required(view_func):
    """
    Decorador que requiere que el usuario esté autenticado y sea un empleado.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Verificar si el usuario tiene un empleado asociado
        if not hasattr(request.user, 'empleado'):
            messages.error(request, 'No tienes permisos para acceder a esta página.')
            return redirect('login')
        
        # Verificar si el empleado está activo
        if not request.user.empleado.activo:
            messages.error(request, 'Tu cuenta de empleado está inactiva.')
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view