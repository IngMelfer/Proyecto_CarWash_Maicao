from django.utils import timezone
from django.db import connection
import pytz

class TimezoneMiddleware:
    """
    Middleware para asegurar que las fechas se manejen correctamente entre Django y MySQL.
    
    Este middleware ayuda a resolver problemas de compatibilidad de zonas horarias
    entre Django (que usa UTC internamente cuando USE_TZ=True) y MySQL.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Antes de procesar la vista
        
        # Verificar la configuración de zona horaria de la conexión MySQL
        self._check_db_timezone()
        
        # Procesar la vista
        response = self.get_response(request)
        
        # Después de procesar la vista
        return response
    
    def _check_db_timezone(self):
        """
        Verifica y ajusta la zona horaria de la conexión MySQL si es necesario.
        """
        try:
            # Solo para conexiones MySQL
            if connection.vendor == 'mysql':
                with connection.cursor() as cursor:
                    # Verificar la zona horaria actual de la sesión
                    cursor.execute("SELECT @@session.time_zone")
                    db_timezone = cursor.fetchone()[0]
                    
                    # Si la zona horaria no está configurada como UTC, configurarla
                    if db_timezone != '+00:00':
                        cursor.execute("SET time_zone = '+00:00'")
        except Exception as e:
            # Registrar el error pero no interrumpir la solicitud
            import logging
            logger = logging.getLogger('django.db.backends')
            logger.warning(f"Error al verificar/configurar la zona horaria de MySQL: {e}")