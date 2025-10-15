from django.shortcuts import render
from reservas.models import Reserva
from django.utils import timezone
from django.db.models import Count

def dashboard_publico(request):
    # Obtener todas las reservas del día actual para contar estadísticas
    todas_reservas_hoy = Reserva.objects.filter(fecha_hora__date=timezone.now().date())
    
    # Obtener solo las reservas activas (no completadas) para mostrar en la tabla
    reservas = todas_reservas_hoy.exclude(estado=Reserva.COMPLETADA).select_related('vehiculo', 'servicio', 'bahia', 'lavador').order_by('fecha_hora')
    
    # Contar reservas por estado usando las constantes correctas del modelo
    confirmados = todas_reservas_hoy.filter(estado=Reserva.CONFIRMADA).count()
    en_proceso = todas_reservas_hoy.filter(estado=Reserva.EN_PROCESO).count()
    completadas = todas_reservas_hoy.filter(estado=Reserva.COMPLETADA).count()
    cancelados = todas_reservas_hoy.filter(estado=Reserva.CANCELADA).count()
    
    # Calcular el total de servicios como la suma de completados + cancelados + confirmados + en proceso
    total_servicios = completadas + cancelados + confirmados + en_proceso
    
    context = {
        'reservas': reservas,
        'confirmados': confirmados,
        'en_proceso': en_proceso,
        'completadas': completadas,
        'cancelados': cancelados,
        'total_servicios': total_servicios
    }
    return render(request, 'dashboard_publico/dashboard.html', context)
