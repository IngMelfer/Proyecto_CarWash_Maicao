#!/usr/bin/env python
"""
Script para crear reservas de prueba para el día de hoy
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from reservas.models import Reserva, Servicio, Bahia, Vehiculo
from clientes.models import Cliente
from empleados.models import Empleado
from django.utils import timezone

def crear_reservas_hoy():
    print("=== CREANDO RESERVAS PARA HOY ===")
    
    # Obtener datos necesarios
    try:
        cliente = Cliente.objects.first()
        servicio = Servicio.objects.first()
        bahia = Bahia.objects.first()
        vehiculo = Vehiculo.objects.first()
        empleado = Empleado.objects.first()
        
        if not all([cliente, servicio, bahia, vehiculo]):
            print("❌ Error: No se encontraron los datos necesarios (cliente, servicio, bahia, vehiculo)")
            return
            
        print(f"✅ Usando cliente: {cliente}")
        print(f"✅ Usando servicio: {servicio}")
        print(f"✅ Usando bahía: {bahia}")
        print(f"✅ Usando vehículo: {vehiculo}")
        
    except Exception as e:
        print(f"❌ Error al obtener datos: {e}")
        return
    
    # Crear reservas para hoy con diferentes estados
    hoy = timezone.now().date()
    ahora = timezone.now()
    
    reservas_crear = [
        {
            'hora': '09:00',
            'estado': Reserva.PENDIENTE,
            'descripcion': 'Pendiente'
        },
        {
            'hora': '10:00', 
            'estado': Reserva.CONFIRMADA,
            'descripcion': 'Confirmada'
        },
        {
            'hora': '11:00',
            'estado': Reserva.EN_PROCESO,
            'descripcion': 'En Proceso'
        },
        {
            'hora': '12:00',
            'estado': Reserva.COMPLETADA,
            'descripcion': 'Completada'
        },
        {
            'hora': '13:00',
            'estado': Reserva.COMPLETADA,
            'descripcion': 'Completada'
        },
        {
            'hora': '14:00',
            'estado': Reserva.EN_PROCESO,
            'descripcion': 'En Proceso'
        }
    ]
    
    reservas_creadas = 0
    
    for reserva_data in reservas_crear:
        try:
            # Crear fecha y hora para hoy
            hora_str = reserva_data['hora']
            hora, minuto = map(int, hora_str.split(':'))
            fecha_hora = datetime.combine(hoy, datetime.min.time().replace(hour=hora, minute=minuto))
            
            # Verificar si ya existe una reserva similar
            existe = Reserva.objects.filter(
                fecha_hora=fecha_hora,
                cliente=cliente,
                servicio=servicio
            ).exists()
            
            if existe:
                print(f"⚠️  Ya existe reserva para {hora_str}")
                continue
            
            # Crear la reserva
            reserva = Reserva.objects.create(
                cliente=cliente,
                servicio=servicio,
                fecha_hora=fecha_hora,
                bahia=bahia,
                vehiculo=vehiculo,
                lavador=empleado if reserva_data['estado'] in [Reserva.EN_PROCESO, Reserva.COMPLETADA] else None,
                estado=reserva_data['estado'],
                notas=f"Reserva de prueba - {reserva_data['descripcion']}"
            )
            
            # Si está completada, agregar fecha de inicio
            if reserva_data['estado'] == Reserva.COMPLETADA:
                reserva.fecha_inicio_servicio = fecha_hora
                reserva.save()
            
            print(f"✅ Creada reserva {reserva_data['descripcion']} para {hora_str}")
            reservas_creadas += 1
            
        except Exception as e:
            print(f"❌ Error creando reserva {reserva_data['hora']}: {e}")
    
    print(f"\n🎉 Se crearon {reservas_creadas} reservas para hoy")
    
    # Verificar el resultado
    print("\n=== VERIFICACIÓN FINAL ===")
    reservas_hoy = Reserva.objects.filter(fecha_hora__date=hoy)
    print(f"Total reservas hoy: {reservas_hoy.count()}")
    print(f"Pendientes: {reservas_hoy.filter(estado=Reserva.PENDIENTE).count()}")
    print(f"Confirmadas: {reservas_hoy.filter(estado=Reserva.CONFIRMADA).count()}")
    print(f"En proceso: {reservas_hoy.filter(estado=Reserva.EN_PROCESO).count()}")
    print(f"Completadas: {reservas_hoy.filter(estado=Reserva.COMPLETADA).count()}")

if __name__ == "__main__":
    crear_reservas_hoy()