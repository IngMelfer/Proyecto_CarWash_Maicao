from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
import json
import logging

logger = logging.getLogger(__name__)

@ensure_csrf_cookie
def csrf_debug_view(request):
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
def csrf_test_ajax(request):
    """
    Vista para probar solicitudes AJAX con protección CSRF.
    """
    try:
        # Registrar información sobre la solicitud para depuración
        logger.info(f"CSRF Test AJAX - Cookies: {request.COOKIES}")
        logger.info(f"CSRF Test AJAX - Headers: {dict(request.headers)}")
        
        # Intentar analizar el cuerpo JSON
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}
            
        # Verificar si la cookie CSRF está presente
        csrf_cookie = request.COOKIES.get('csrftoken')
        csrf_header = request.META.get('HTTP_X_CSRFTOKEN')
        
        return JsonResponse({
            'success': True,
            'message': 'Solicitud AJAX procesada correctamente',
            'csrf_cookie_present': csrf_cookie is not None,
            'csrf_header_present': csrf_header is not None,
            'received_data': data
        })
    except Exception as e:
        logger.exception("Error en la vista csrf_test_ajax")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)