import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from reservas.models import Reserva
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from clientes.models import Cliente

# Obtener la reserva
reserva = Reserva.objects.get(id=6)
print(f"Reserva: {reserva}")
print(f"Estado: {reserva.estado}")
print(f"Fecha inicio servicio: {reserva.fecha_inicio_servicio}")
print(f"Duración servicio: {reserva.servicio.duracion_minutos}")

# Verificar el formato de fecha para el template
if reserva.fecha_inicio_servicio:
    fecha_formateada = reserva.fecha_inicio_servicio.strftime("%Y-%m-%d %H:%M:%S")
    print(f"Fecha formateada para template: {fecha_formateada}")
else:
    print("PROBLEMA: fecha_inicio_servicio es None")

print("Script completado")