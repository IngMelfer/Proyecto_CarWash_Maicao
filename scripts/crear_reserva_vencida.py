# Script para crear una reserva vencida
# Ejecutar con: python manage.py shell < scripts/crear_reserva_vencida.py

from django.utils import timezone
from datetime import timedelta
from reservas.models import Reserva, Servicio, Bahia
from clientes.models import Cliente

# Obtener un cliente y un servicio existente
cliente = Cliente.objects.first()
if not cliente:
    print("No hay clientes en la base de datos")
    exit(1)

servicio = Servicio.objects.first()
if not servicio:
    print("No hay servicios en la base de datos")
    exit(1)

# Obtener una bahía disponible
bahia = Bahia.objects.filter(activo=True).first()
if not bahia:
    print("No hay bahías disponibles en el sistema")
    exit(1)

# Crear una reserva con fecha en el pasado (hace 2 horas)
fecha_pasada = timezone.now() - timedelta(hours=2)

# Verificar si ya existe una reserva con la misma fecha_hora y bahia
reserva_existente = Reserva.objects.filter(fecha_hora=fecha_pasada, bahia=bahia).exists()
if reserva_existente:
    # Si ya existe, modificar ligeramente la fecha para evitar conflicto
    fecha_pasada = fecha_pasada + timedelta(minutes=1)
    print("Se ajustó la fecha para evitar conflicto con reserva existente")

# Crear la reserva
reserva = Reserva.objects.create(
    cliente=cliente,
    servicio=servicio,
    fecha_hora=fecha_pasada,
    bahia=bahia,  # Asignar la bahía
    estado=Reserva.PENDIENTE,
    notas='Reserva de prueba para verificar el sistema de incumplimiento'
)

print(f'Reserva vencida creada con ID {reserva.id} para {cliente} - {servicio}')
print(f'Fecha y hora: {fecha_pasada}')
print('Ejecute el comando "python manage.py verificar_reservas_vencidas" para marcarla como incumplida')