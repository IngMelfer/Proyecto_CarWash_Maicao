import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

# Importar después de configurar Django
from django.utils import timezone
from datetime import timedelta
from reservas.models import Reserva, Servicio
from clientes.models import Cliente

# Obtener un cliente y un servicio existente
cliente = Cliente.objects.first()
servicio = Servicio.objects.first()

# Crear una reserva con fecha en el pasado (hace 2 horas)
fecha_pasada = timezone.now() - timedelta(hours=2)

# Crear la reserva
reserva = Reserva.objects.create(
    cliente=cliente,
    servicio=servicio,
    fecha_hora=fecha_pasada,
    estado=Reserva.PENDIENTE,
    notas='Reserva de prueba para verificar el sistema de incumplimiento'
)

print(f'Reserva vencida creada con ID {reserva.id} para {cliente} - {servicio}')
print(f'Fecha y hora: {fecha_pasada}')
print('Ejecute el comando "python manage.py verificar_reservas_vencidas" para marcarla como incumplida')