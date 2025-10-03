#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from reservas.models import Reserva, Bahia

print("=== VERIFICACIÓN DE RESERVAS Y TOKENS ===")
print()

# Verificar bahías
print("BAHÍAS CONFIGURADAS:")
bahias = Bahia.objects.all()
for bahia in bahias:
    print(f"- {bahia.nombre}: tiene_camara={bahia.tiene_camara}, ip_camara={bahia.ip_camara}")
print()

# Verificar reservas activas
print("RESERVAS ACTIVAS:")
reservas = Reserva.objects.all().select_related('cliente__usuario', 'bahia')
for reserva in reservas:
    cliente_name = reserva.cliente.usuario.username if reserva.cliente else "Sin cliente"
    bahia_name = reserva.bahia.nombre if reserva.bahia else "Sin bahía"
    print(f"- ID {reserva.id}: {cliente_name} en {bahia_name} - Estado: {reserva.estado} - Token: {reserva.stream_token}")
print()

# Verificar reservas con bahías que tienen cámara pero sin token
print("RESERVAS CON BAHÍAS CON CÁMARA PERO SIN TOKEN:")
reservas_sin_token = Reserva.objects.filter(
    bahia__tiene_camara=True,
    stream_token__isnull=True
).select_related('cliente__usuario', 'bahia')

for reserva in reservas_sin_token:
    cliente_name = reserva.cliente.usuario.username if reserva.cliente else "Sin cliente"
    ip_camara = reserva.bahia.ip_camara if reserva.bahia.ip_camara else "Sin IP"
    print(f"- ID {reserva.id}: {cliente_name} en {reserva.bahia.nombre} - Estado: {reserva.estado} - IP: {ip_camara}")
print()

print("=== FIN DE VERIFICACIÓN ===")