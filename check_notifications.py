#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from notificaciones.models import Notificacion
from empleados.models import Empleado
from autenticacion.models import Usuario

print("=== VERIFICACIÓN DE NOTIFICACIONES ===")

# Verificar notificaciones no leídas para empleados
notifs_empleados = Notificacion.objects.filter(empleado__isnull=False, leida=False)
print(f"Total notificaciones no leídas para empleados: {notifs_empleados.count()}")

for n in notifs_empleados:
    print(f"ID: {n.id}")
    print(f"Empleado: {n.empleado.nombre_completo if n.empleado else 'None'}")
    print(f"Usuario: {n.empleado.usuario.username if n.empleado and n.empleado.usuario else 'None'}")
    print(f"Tipo: {n.tipo}")
    print(f"Título: {n.titulo}")
    print(f"Mensaje: {n.mensaje[:50]}...")
    print(f"Leída: {n.leida}")
    print(f"Fecha: {n.fecha_creacion}")
    print("-" * 50)

# Verificar todos los empleados
print("\n=== EMPLEADOS REGISTRADOS ===")
empleados = Empleado.objects.all()
print(f"Total empleados: {empleados.count()}")

for emp in empleados:
    print(f"ID: {emp.id}")
    print(f"Nombre: {emp.nombre_completo}")
    print(f"Usuario: {emp.usuario.username if emp.usuario else 'Sin usuario'}")
    print(f"Cargo: {emp.cargo.nombre if emp.cargo else 'Sin cargo'}")
    print("-" * 30)

# Verificar todas las notificaciones
print("\n=== TODAS LAS NOTIFICACIONES ===")
todas_notifs = Notificacion.objects.all().order_by('-fecha_creacion')
print(f"Total notificaciones: {todas_notifs.count()}")

for n in todas_notifs[:10]:  # Solo las últimas 10
    print(f"ID: {n.id}")
    print(f"Cliente: {n.cliente.usuario.get_full_name() if n.cliente else 'None'}")
    print(f"Empleado: {n.empleado.nombre_completo if n.empleado else 'None'}")
    print(f"Tipo: {n.tipo}")
    print(f"Título: {n.titulo}")
    print(f"Leída: {n.leida}")
    print(f"Fecha: {n.fecha_creacion}")
    print("-" * 30)