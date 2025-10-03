from django.shortcuts import render
from reservas.models import Reserva
from django.utils import timezone

def dashboard_publico(request):
    reservas = Reserva.objects.filter(fecha_hora__date=timezone.now().date()).select_related('vehiculo', 'servicio', 'bahia', 'lavador').order_by('fecha_hora')
    context = {
        'reservas': reservas
    }
    return render(request, 'dashboard_publico/dashboard.html', context)
