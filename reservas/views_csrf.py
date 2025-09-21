from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
import json
import logging

logger = logging.getLogger(__name__)

@ensure_csrf_cookie
def csrf_diagnostico_view(request):
    """
    Vista para la página de diagnóstico de problemas CSRF.
    El decorador ensure_csrf_cookie garantiza que se establezca la cookie CSRF.
    """
    # Registrar información sobre la solicitud para depuración
    logger.info(f"CSRF Debug View - Cookies: {request.COOKIES}")
    logger.info(f"CSRF Debug View - Headers: {dict(request.headers)}")
    
    # Verificar si la cookie CSRF está presente
    csrf_cookie = request.COOKIES.get('csrftoken')
    csrf_present = csrf_cookie is not None
    
    context = {
        'csrf_present': csrf_present,
        'csrf_token': csrf_cookie[:10] + '...' if csrf_present else 'No disponible',
    }
    
    return render(request, 'csrf_debug.html', context)

@require_POST
def csrf_test_view(request):
    """
    Vista de prueba para verificar que el token CSRF funciona correctamente.
    """
    try:
        # Obtener datos del POST
        data = json.loads(request.body) if request.body else {}
        
        # Registrar información para depuración
        logger.info(f"CSRF Test - Data: {data}")
        logger.info(f"CSRF Test - Headers: {dict(request.headers)}")
        
        return JsonResponse({
            'success': True,
            'message': 'Token CSRF válido',
            'data': data
        })
    except Exception as e:
        logger.error(f"Error en csrf_test_view: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)