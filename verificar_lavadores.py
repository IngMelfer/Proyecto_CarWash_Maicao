#!/usr/bin/env python
"""
Script para verificar el estado de los lavadores en las reservas
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from reservas.models import Reserva

def verificar_reservas():
    print("=== VERIFICACIÓN DE LAVADORES EN RESERVAS ===\n")
    
    # Verificar reservas en proceso
    reservas_proceso = Reserva.objects.filter(estado='PR')
    print(f"Total reservas en proceso: {reservas_proceso.count()}")
    
    if reservas_proceso.exists():
        print("\nReservas en proceso:")
        for r in reservas_proceso[:10]:
            lavador_info = r.lavador.nombre_completo() if r.lavador else "Sin asignar"
            print(f"  ID: {r.id}, Cliente: {r.cliente}, Lavador: {lavador_info}")
    
    # Verificar reservas sin lavador
    reservas_sin_lavador = Reserva.objects.filter(
        estado__in=['PE', 'CO', 'PR'], 
        lavador__isnull=True
    )
    print(f"\nReservas sin lavador asignado: {reservas_sin_lavador.count()}")
    
    if reservas_sin_lavador.exists():
        print("\nReservas sin lavador:")
        for r in reservas_sin_lavador[:10]:
            print(f"  ID: {r.id}, Cliente: {r.cliente}, Estado: {r.get_estado_display()}")
    
    # Verificar empleados lavadores disponibles
    from empleados.models import Empleado
    lavadores = Empleado.objects.filter(
        rol=Empleado.ROL_LAVADOR,
        activo=True,
        disponible=True
    )
    print(f"\nLavadores disponibles: {lavadores.count()}")
    
    if lavadores.exists():
        print("\nLavadores activos y disponibles:")
        for l in lavadores:
            print(f"  ID: {l.id}, Nombre: {l.nombre_completo()}")

if __name__ == "__main__":
    verificar_reservas()