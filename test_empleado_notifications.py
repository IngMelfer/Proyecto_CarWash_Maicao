#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from empleados.models import Empleado
from notificaciones.models import Notificacion

def test_empleado_notifications():
    print("=== VERIFICANDO NOTIFICACIONES PARA EMPLEADOS ===")
    
    # Buscar empleados
    empleados = Empleado.objects.all()
    print(f"\nEmpleados encontrados: {empleados.count()}")
    
    for empleado in empleados:
        print(f"\n--- Empleado: {empleado.usuario.username} ---")
        print(f"Nombre: {empleado.usuario.first_name} {empleado.usuario.last_name}")
        print(f"Email: {empleado.usuario.email}")
        
        # Verificar notificaciones del empleado
        notificaciones_empleado = Notificacion.objects.filter(empleado=empleado)
        print(f"Total notificaciones: {notificaciones_empleado.count()}")
        
        # Notificaciones no leídas
        no_leidas = notificaciones_empleado.filter(leida=False)
        print(f"Notificaciones no leídas: {no_leidas.count()}")
        
        # Notificaciones por tipo
        calificaciones = notificaciones_empleado.filter(tipo=Notificacion.CALIFICACION_RECIBIDA)
        servicios = notificaciones_empleado.filter(tipo=Notificacion.SERVICIO_ASIGNADO)
        
        print(f"Calificaciones recibidas: {calificaciones.count()}")
        print(f"Servicios asignados: {servicios.count()}")
        
        # Mostrar las últimas 3 notificaciones no leídas
        if no_leidas.exists():
            print("\nÚltimas notificaciones no leídas:")
            for notif in no_leidas.order_by('-fecha_creacion')[:3]:
                print(f"  - ID: {notif.id}, Tipo: {notif.get_tipo_display()}, Título: {notif.titulo}")
                print(f"    Mensaje: {notif.mensaje[:50]}...")
                print(f"    Fecha: {notif.fecha_creacion}")
        else:
            print("No hay notificaciones no leídas")
    
    # Verificar constantes del modelo
    print("\n=== CONSTANTES DEL MODELO ===")
    print("CALIFICACION_RECIBIDA: '{}'".format(Notificacion.CALIFICACION_RECIBIDA))
    print("SERVICIO_ASIGNADO: '{}'".format(Notificacion.SERVICIO_ASIGNADO))
    
    # Verificar todas las notificaciones de empleados
    print("\n=== TODAS LAS NOTIFICACIONES DE EMPLEADOS ===")
    notifs_empleados = Notificacion.objects.filter(empleado__isnull=False)
    print(f"Total notificaciones de empleados: {notifs_empleados.count()}")
    
    tipos_empleados = notifs_empleados.filter(
        tipo__in=[Notificacion.CALIFICACION_RECIBIDA, Notificacion.SERVICIO_ASIGNADO]
    )
    print(f"Notificaciones de tipos válidos para empleados: {tipos_empleados.count()}")
    
    no_leidas_empleados = tipos_empleados.filter(leida=False)
    print(f"Notificaciones no leídas de empleados: {no_leidas_empleados.count()}")

if __name__ == "__main__":
    test_empleado_notifications()