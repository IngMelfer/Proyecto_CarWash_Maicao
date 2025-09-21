import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from reservas.models import Reserva
from clientes.models import Cliente
from datetime import datetime, timezone

# Obtener la reserva específica
try:
    reserva = Reserva.objects.get(id=6)
    print(f"Reserva ID: {reserva.id}")
    print(f"Estado: {reserva.estado}")
    print(f"Fecha hora: {reserva.fecha_hora}")
    print(f"Fecha inicio servicio: {reserva.fecha_inicio_servicio}")
    print(f"Servicio: {reserva.servicio.nombre}")
    print(f"Duración servicio: {reserva.servicio.duracion_minutos} minutos")
    
    # Verificar si tiene fecha_inicio_servicio
    if reserva.fecha_inicio_servicio:
        print(f"Fecha inicio servicio completa: {reserva.fecha_inicio_servicio}")
        
        # Verificar si está en el pasado o futuro
        ahora = datetime.now(timezone.utc)
        print(f"Ahora: {ahora}")
        print(f"¿Es pasado?: {reserva.fecha_inicio_servicio < ahora}")
        
        # Formato para JavaScript (como en el template)
        fecha_js = reserva.fecha_inicio_servicio.strftime('%Y-%m-%d %H:%M:%S')
        print(f"Fecha formato JS: {fecha_js}")
        
        # Calcular tiempo transcurrido y restante
        tiempo_transcurrido = ahora - reserva.fecha_inicio_servicio.replace(tzinfo=timezone.utc)
        duracion_total_segundos = reserva.servicio.duracion_minutos * 60
        tiempo_transcurrido_segundos = tiempo_transcurrido.total_seconds()
        tiempo_restante_segundos = duracion_total_segundos - tiempo_transcurrido_segundos
        
        print(f"Tiempo transcurrido: {tiempo_transcurrido_segundos} segundos")
        print(f"Duración total: {duracion_total_segundos} segundos")
        print(f"Tiempo restante: {tiempo_restante_segundos} segundos")
        
        if tiempo_restante_segundos > 0:
            minutos_restantes = int(tiempo_restante_segundos // 60)
            segundos_restantes = int(tiempo_restante_segundos % 60)
            print(f"Tiempo restante formateado: {minutos_restantes:02d}:{segundos_restantes:02d}")
        else:
            print("TIEMPO AGOTADO")
        
    else:
        print("PROBLEMA: fecha_inicio_servicio es None")
        
except Reserva.DoesNotExist:
    print("Reserva no encontrada")
except Exception as e:
    print(f"Error: {e}")

print("Script completado")