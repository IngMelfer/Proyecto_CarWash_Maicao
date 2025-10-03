from django.shortcuts import render
from reservas.models import Reserva
from django.utils import timezone
from django.db.models import Count

def dashboard_publico(request):
    # Obtener todas las reservas del día actual
    reservas = Reserva.objects.filter(fecha_hora__date=timezone.now().date()).select_related('vehiculo', 'servicio', 'bahia', 'lavador').order_by('fecha_hora')
    
    # Contar reservas por estado
    pendientes = reservas.filter(estado='pendiente').count()
    en_proceso = reservas.filter(estado='en_proceso').count()
    completadas = reservas.filter(estado='completado').count()
    
    context = {
        'reservas': reservas,
        'pendientes': pendientes,
        'en_proceso': en_proceso,
        'completadas': completadas
    }
    return render(request, 'dashboard_publico/dashboard.html', context)
