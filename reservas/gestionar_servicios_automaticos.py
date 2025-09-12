from django.utils import timezone
from .models import Reserva

def iniciar_servicios_pendientes():
    """
    Función para iniciar automáticamente los servicios que están confirmados
    y cuya hora de inicio ya ha pasado.
    """
    # Obtener la hora actual
    ahora = timezone.now()
    
    # Buscar reservas confirmadas cuya hora de inicio ya ha pasado
    reservas_pendientes = Reserva.objects.filter(
        estado=Reserva.CONFIRMADA,
        fecha_hora__lte=ahora
    )
    
    servicios_iniciados = 0
    
    # Iniciar cada servicio pendiente
    for reserva in reservas_pendientes:
        try:
            # Iniciar el servicio
            if reserva.iniciar_servicio():
                reserva.fecha_inicio_servicio = ahora
                reserva.save(update_fields=['fecha_inicio_servicio'])
                servicios_iniciados += 1
                print(f"Servicio iniciado automáticamente: {reserva}")
        except Exception as e:
            print(f"Error al iniciar servicio automáticamente: {str(e)}")
    
    return servicios_iniciados