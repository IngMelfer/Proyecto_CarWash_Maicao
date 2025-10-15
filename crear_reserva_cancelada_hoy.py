#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from reservas.models import Reserva, Servicio, MedioPago
from clientes.models import Cliente
from datetime import datetime, date
from django.utils import timezone

def crear_reserva_cancelada_hoy():
    """
    Crea una reserva cancelada para hoy para poder verificar el dashboard
    """
    try:
        # Obtener un cliente existente
        cliente = Cliente.objects.first()
        if not cliente:
            print("❌ No hay clientes en la base de datos")
            return False
        
        # Obtener un servicio existente
        servicio = Servicio.objects.first()
        if not servicio:
            print("❌ No hay servicios en la base de datos")
            return False
        
        # Obtener un medio de pago
        medio_pago = MedioPago.objects.first()
        if not medio_pago:
            print("❌ No hay medios de pago en la base de datos")
            return False
        
        # Crear fecha y hora para hoy
        hoy = date.today()
        fecha_hora = datetime.combine(hoy, datetime.now().time())
        
        # Crear la reserva cancelada
        reserva = Reserva.objects.create(
            cliente=cliente,
            servicio=servicio,
            fecha_hora=fecha_hora,
            estado=Reserva.CANCELADA,
            medio_pago=medio_pago,
            precio_final=servicio.precio,
            notas="Reserva de prueba cancelada para verificar dashboard"
        )
        
        print(f"✅ Reserva cancelada creada exitosamente:")
        print(f"   ID: {reserva.id}")
        print(f"   Cliente: {reserva.cliente}")
        print(f"   Servicio: {reserva.servicio}")
        print(f"   Fecha: {reserva.fecha_hora.date()}")
        print(f"   Estado: {reserva.get_estado_display()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear la reserva: {e}")
        return False

if __name__ == "__main__":
    print("=== CREANDO RESERVA CANCELADA PARA HOY ===")
    
    # Verificar si ya hay reservas canceladas hoy
    canceladas_hoy = Reserva.objects.filter(
        fecha_hora__date=date.today(), 
        estado=Reserva.CANCELADA
    ).count()
    
    print(f"Reservas canceladas hoy antes: {canceladas_hoy}")
    
    if crear_reserva_cancelada_hoy():
        # Verificar después de crear
        canceladas_hoy_despues = Reserva.objects.filter(
            fecha_hora__date=date.today(), 
            estado=Reserva.CANCELADA
        ).count()
        print(f"Reservas canceladas hoy después: {canceladas_hoy_despues}")
        print("\n🎯 Ahora puedes verificar el dashboard público")
    else:
        print("❌ No se pudo crear la reserva cancelada")