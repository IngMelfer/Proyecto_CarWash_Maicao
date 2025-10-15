#!/usr/bin/env python
"""
Script para verificar el estado de las reservas en la base de datos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from reservas.models import Reserva
from django.utils import timezone

def verificar_reservas():
    print("=== VERIFICACIÓN DE RESERVAS ===")
    print(f"Total reservas: {Reserva.objects.count()}")
    print(f"Reservas PENDIENTES (PE): {Reserva.objects.filter(estado='PE').count()}")
    print(f"Reservas CONFIRMADAS (CO): {Reserva.objects.filter(estado='CO').count()}")
    print(f"Reservas EN_PROCESO (PR): {Reserva.objects.filter(estado='PR').count()}")
    print(f"Reservas COMPLETADAS (CM): {Reserva.objects.filter(estado='CM').count()}")
    print(f"Reservas CANCELADAS (CA): {Reserva.objects.filter(estado='CA').count()}")
    print(f"Reservas INCUMPLIDAS (IN): {Reserva.objects.filter(estado='IN').count()}")
    
    print("\n=== RESERVAS DE HOY ===")
    hoy = timezone.now().date()
    reservas_hoy = Reserva.objects.filter(fecha_hora__date=hoy)
    print(f"Total reservas hoy: {reservas_hoy.count()}")
    print(f"Pendientes hoy: {reservas_hoy.filter(estado='PE').count()}")
    print(f"Confirmadas hoy: {reservas_hoy.filter(estado='CO').count()}")
    print(f"En proceso hoy: {reservas_hoy.filter(estado='PR').count()}")
    print(f"Completadas hoy: {reservas_hoy.filter(estado='CM').count()}")
    
    print("\n=== ÚLTIMAS 5 RESERVAS ===")
    ultimas_reservas = Reserva.objects.all().order_by('-fecha_creacion')[:5]
    for reserva in ultimas_reservas:
        print(f"ID: {reserva.id}, Estado: {reserva.estado} ({reserva.get_estado_display()}), Fecha: {reserva.fecha_hora}, Creada: {reserva.fecha_creacion}")

if __name__ == "__main__":
    verificar_reservas()