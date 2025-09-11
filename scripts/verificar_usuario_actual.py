#!/usr/bin/env python
"""
Script para verificar el usuario actual y sus servicios.
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

# Importar después de configurar Django
from autenticacion.models import Usuario
from clientes.models import Cliente, HistorialServicio
from reservas.models import Reserva

# Listar todos los usuarios y sus clientes asociados
print("\n=== USUARIOS Y CLIENTES ===")
for usuario in Usuario.objects.all():
    cliente = getattr(usuario, 'cliente', None)
    print(f"Usuario: {usuario.username} (ID: {usuario.id})")
    print(f"  Es staff: {usuario.is_staff}")
    print(f"  Cliente asociado: {cliente}")
    
    if cliente:
        # Verificar historial de servicios
        historial = HistorialServicio.objects.filter(cliente=cliente)
        print(f"  Servicios en historial: {historial.count()}")
        
        # Mostrar los servicios
        if historial.exists():
            print("  Servicios:")
            for servicio in historial:
                print(f"    - {servicio.servicio} ({servicio.fecha_servicio})")
                
                # Buscar la reserva asociada
                reserva = Reserva.objects.filter(
                    cliente=cliente,
                    fecha_hora=servicio.fecha_servicio,
                    servicio__nombre=servicio.servicio
                ).first()
                
                if reserva:
                    print(f"      Reserva: {reserva.id} - Vehículo: {reserva.vehiculo if reserva.vehiculo else 'No especificado'}")
                else:
                    print("      No se encontró reserva asociada")
        else:
            print("  No tiene servicios en el historial")
    print()

print("\n=== CLIENTES SIN USUARIO ===")
for cliente in Cliente.objects.filter(usuario__isnull=True):
    print(f"Cliente: {cliente}")
    historial = HistorialServicio.objects.filter(cliente=cliente)
    print(f"  Servicios en historial: {historial.count()}")