#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

# Importar después de configurar Django
from clientes.models import Cliente, HistorialServicio
from reservas.models import Vehiculo

def crear_datos_prueba():
    try:
        # Obtener el vehículo con ID 1
        vehiculo = Vehiculo.objects.get(id=1)
        cliente = vehiculo.cliente
        
        print(f"Creando datos de prueba para vehículo: {vehiculo.marca} {vehiculo.modelo} - {vehiculo.placa}")
        print(f"Cliente: {cliente.nombre} {cliente.apellido}")
        
        # Crear varios servicios de prueba
        servicios_prueba = [
            {
                'servicio': 'Lavado Básico',
                'descripcion': 'Lavado exterior completo del vehículo',
                'monto': Decimal('15000'),
                'puntos_ganados': 15,
                'fecha_servicio': datetime.now() - timedelta(days=30),
                'comentarios': 'Servicio realizado satisfactoriamente'
            },
            {
                'servicio': 'Lavado Premium',
                'descripcion': 'Lavado completo interior y exterior',
                'monto': Decimal('25000'),
                'puntos_ganados': 25,
                'fecha_servicio': datetime.now() - timedelta(days=15),
                'comentarios': 'Excelente servicio, muy recomendado'
            },
            {
                'servicio': 'Encerado',
                'descripcion': 'Aplicación de cera protectora',
                'monto': Decimal('35000'),
                'puntos_ganados': 35,
                'fecha_servicio': datetime.now() - timedelta(days=7),
                'comentarios': 'El vehículo quedó brillante'
            },
            {
                'servicio': 'Detallado Completo',
                'descripcion': 'Servicio completo de detallado profesional',
                'monto': Decimal('50000'),
                'puntos_ganados': 50,
                'fecha_servicio': datetime.now() - timedelta(days=2),
                'comentarios': 'Servicio premium, excelente calidad'
            }
        ]
        
        # Crear los registros de historial
        for servicio_data in servicios_prueba:
            historial, created = HistorialServicio.objects.get_or_create(
                cliente=cliente,
                servicio=servicio_data['servicio'],
                fecha_servicio=servicio_data['fecha_servicio'],
                defaults={
                    'descripcion': servicio_data['descripcion'],
                    'monto': servicio_data['monto'],
                    'puntos_ganados': servicio_data['puntos_ganados'],
                    'comentarios': servicio_data['comentarios']
                }
            )
            
            if created:
                print(f"✓ Creado: {servicio_data['servicio']} - ${servicio_data['monto']}")
            else:
                print(f"- Ya existe: {servicio_data['servicio']}")
        
        # Mostrar resumen
        total_servicios = HistorialServicio.objects.filter(cliente=cliente).count()
        print(f"\nResumen:")
        print(f"Total de servicios en historial: {total_servicios}")
        print(f"Datos de prueba creados exitosamente!")
        
    except Vehiculo.DoesNotExist:
        print("Error: No se encontró el vehículo con ID 1")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    crear_datos_prueba()