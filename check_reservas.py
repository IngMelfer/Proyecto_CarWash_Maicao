#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from reservas.models import Reserva
from django.contrib.auth.models import User
from clientes.models import Cliente

print("=== VERIFICACIÓN DE RESERVAS ===")
print(f"Total reservas en BD: {Reserva.objects.count()}")
print(f"Total usuarios: {User.objects.count()}")
print(f"Total clientes: {Cliente.objects.count()}")

if User.objects.exists():
    user = User.objects.first()
    print(f"\nPrimer usuario: {user.username}")
    
    if hasattr(user, 'cliente'):
        cliente = user.cliente
        print(f"Cliente: {cliente}")
        reservas_cliente = Reserva.objects.filter(cliente=cliente)
        print(f"Reservas del cliente: {reservas_cliente.count()}")
        
        if reservas_cliente.exists():
            print("\nReservas encontradas:")
            for reserva in reservas_cliente:
                print(f"- ID: {reserva.id}, Estado: {reserva.estado}, Fecha: {reserva.fecha_hora}")
        else:
            print("No se encontraron reservas para este cliente")
    else:
        print("El usuario no tiene perfil de cliente")

print("\n=== TODAS LAS RESERVAS ===")
for reserva in Reserva.objects.all():
    print(f"ID: {reserva.id}, Cliente: {reserva.cliente}, Estado: {reserva.estado}, Fecha: {reserva.fecha_hora}")