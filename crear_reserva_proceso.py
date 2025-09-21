#!/usr/bin/env python
"""
Script para crear una reserva en proceso para testing del cronómetro
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from clientes.models import Cliente
from reservas.models import Reserva, Servicio, Vehiculo, Bahia

User = get_user_model()

def crear_reserva_proceso():
    """Crear una reserva en proceso para testing"""
    try:
        # Obtener el cliente
        usuario = User.objects.first()
        cliente = usuario.cliente
        print(f"Cliente: {cliente}")
        
        # Obtener o crear un servicio
        servicio, created = Servicio.objects.get_or_create(
            nombre="Lavado General - Sencillo",
            defaults={
                'descripcion': 'Lavado básico del vehículo',
                'precio': 20000.00,
                'duracion_minutos': 30,
                'activo': True
            }
        )
        print(f"Servicio: {servicio}")
        
        # Crear o obtener un vehículo
        vehiculo, created = Vehiculo.objects.get_or_create(
            cliente=cliente,
            placa='PROC123',
            defaults={
                'marca': 'Toyota',
                'modelo': 'Corolla',
                'anio': 2020,
                'color': 'Blanco',
                'tipo': 'AU'
            }
        )
        print(f"Vehículo: {vehiculo}")
        
        # Obtener o crear una bahía
        bahia, created = Bahia.objects.get_or_create(
            nombre="Bahía 2",
            defaults={
                'descripcion': 'Bahía de lavado 2',
                'activa': True
            }
        )
        print(f"Bahía: {bahia}")
        
        # Crear la reserva en proceso
        ahora = timezone.now()
        fecha_inicio = ahora - timedelta(minutes=10)  # Comenzó hace 10 minutos
        
        reserva = Reserva.objects.create(
            cliente=cliente,
            servicio=servicio,
            vehiculo=vehiculo,
            bahia=bahia,
            fecha_hora=fecha_inicio,
            estado=Reserva.EN_PROCESO,
            fecha_inicio_servicio=fecha_inicio,
            precio_final=servicio.precio
        )
        
        print(f"Reserva en proceso creada: {reserva}")
        print(f"Estado: {reserva.estado}")
        print(f"Fecha inicio: {reserva.fecha_inicio_servicio}")
        print(f"Duración servicio: {servicio.duracion_minutos} minutos")
        
        return reserva
        
    except Exception as e:
        print(f"Error al crear reserva: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    crear_reserva_proceso()