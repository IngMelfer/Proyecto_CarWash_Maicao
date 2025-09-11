from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
import json
import logging

logger = logging.getLogger(__name__)

@ensure_csrf_cookie
def csrf_diagnostico_view(request):
    """
    Vista para la página de diagnóstico de CSRF.
    Asegura que se establezca la cookie CSRF.
    """
    # Registrar información de la solicitud para diagnóstico
    logger.info(f"CSRF Diagnóstico - User Agent: {request.META.get('HTTP_USER_AGENT')}")
    logger.info(f"CSRF Diagnóstico - Cookies: {request.COOKIES}")
    logger.info(f"CSRF Diagnóstico - Headers: {dict(request.headers)}")
    
    # Verificar si la cookie CSRF está presente
    csrf_cookie = request.COOKIES.get('csrftoken')
    if csrf_cookie:
        logger.info(f"CSRF Diagnóstico - Cookie CSRF encontrada: {csrf_cookie[:10]}...")
    else:
        logger.warning("CSRF Diagnóstico - Cookie CSRF NO encontrada")
    
    return render(request, 'reservas/csrf_diagnostico.html')

@require_POST
def csrf_test_view(request):
    """
    Vista para probar la funcionalidad CSRF.
    Acepta solicitudes POST y devuelve una respuesta JSON.
    """
    try:
        # Registrar información de la solicitud para diagnóstico
        logger.info(f"CSRF Test - Method: {request.method}")
        logger.info(f"CSRF Test - Content Type: {request.content_type}")
        logger.info(f"CSRF Test - Headers: {dict(request.headers)}")
        
        # Procesar datos según el tipo de contenido
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                logger.info(f"CSRF Test - JSON Data: {data}")
                return JsonResponse({
                    'success': True,
                    'message': 'Solicitud AJAX procesada correctamente',
                    'received_data': data
                })
            except json.JSONDecodeError as e:
                logger.error(f"CSRF Test - Error al decodificar JSON: {e}")
                return JsonResponse({
                    'success': False,
                    'error': 'Error al decodificar JSON'
                }, status=400)
        else:
            # Formulario normal
            logger.info(f"CSRF Test - Form Data: {request.POST}")
            return JsonResponse({
                'success': True,
                'message': 'Formulario procesado correctamente',
                'received_data': dict(request.POST)
            })
    except Exception as e:
        logger.exception(f"CSRF Test - Error inesperado: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)