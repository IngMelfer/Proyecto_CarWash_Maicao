#!/usr/bin/env python
"""
Script para crear servicios de prueba en el historial.
"""

import os
import sys
import django
from django.utils import timezone
from datetime import timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

# Importar después de configurar Django
from clientes.models import Cliente, HistorialServicio
from reservas.models import Vehiculo, Reserva, Servicio

# Obtener el primer cliente
cliente = Cliente.objects.first()

if cliente:
    # Obtener o crear un vehículo para el cliente
    vehiculo = Vehiculo.objects.filter(cliente=cliente).first()
    if not vehiculo:
        vehiculo = Vehiculo.objects.create(
            cliente=cliente,
            marca='Toyota',
            modelo='Corolla',
            anio=2020,
            placa='ABC123',
            color='Blanco'
        )
        print(f'Vehículo creado para el cliente {cliente}')
    
    # Crear servicios de prueba en el historial
    servicios = [
        {
            'nombre': 'Lavado Premium',
            'descripcion': 'Lavado completo con encerado',
            'dias_atras': 2,
            'monto': 50.00,
            'puntos': 5
        },
        {
            'nombre': 'Detallado Interior',
            'descripcion': 'Limpieza profunda de interiores',
            'dias_atras': 10,
            'monto': 75.00,
            'puntos': 7
        },
        {
            'nombre': 'Pulido de Carrocería',
            'descripcion': 'Pulido y tratamiento de pintura',
            'dias_atras': 20,
            'monto': 120.00,
            'puntos': 12
        }
    ]
    
    # Crear un servicio en el sistema para asociarlo a las reservas
    servicio_sistema, created = Servicio.objects.get_or_create(
        nombre='Lavado Premium',
        defaults={
            'descripcion': 'Lavado completo con encerado',
            'precio': 50.00,
            'duracion_minutos': 60,
            'puntos_otorgados': 5
        }
    )
    
    for s in servicios:
        # Crear fecha del servicio
        fecha_servicio = timezone.now() - timedelta(days=s['dias_atras'])
        
        # Crear una reserva asociada (para que se pueda vincular el vehículo)
        reserva = Reserva.objects.create(
            cliente=cliente,
            servicio=servicio_sistema,
            vehiculo=vehiculo,
            fecha_hora=fecha_servicio,
            estado=Reserva.COMPLETADA
        )
        
        # Crear el historial de servicio
        historial = HistorialServicio.objects.create(
            cliente=cliente,
            servicio=s['nombre'],
            descripcion=s['descripcion'],
            fecha_servicio=fecha_servicio,
            monto=s['monto'],
            puntos_ganados=s['puntos'],
            comentarios='Servicio completado satisfactoriamente'
        )
        
        print(f'Servicio "{s["nombre"]}" creado para el cliente {cliente}')
    
    print('\nServicios de prueba creados exitosamente')
else:
    print('No se encontró ningún cliente en la base de datos')