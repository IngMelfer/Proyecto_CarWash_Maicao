#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from empleados.models import Cargo, Empleado
from autenticacion.models import Usuario

print("=== VERIFICACIÓN DE CARGOS Y EMPLEADOS ===")

# Verificar cargos disponibles
print("\nCargos disponibles:")
cargos = Cargo.objects.all()
for c in cargos:
    print(f"  - Código: '{c.codigo}', Nombre: '{c.nombre}', Activo: {c.activo}")

# Verificar empleados y sus cargos
print("\nEmpleados y sus cargos:")
empleados = Empleado.objects.all()
for e in empleados:
    print(f"  - {e.nombre} {e.apellido}: Cargo código '{e.cargo.codigo}' ({e.cargo.nombre})")
    print(f"    Usuario: {e.usuario.email}, Rol: {e.usuario.rol}")

# Verificar usuarios con rol lavador
print("\nUsuarios con rol lavador:")
usuarios_lavador = Usuario.objects.filter(rol=Usuario.ROL_LAVADOR)
for u in usuarios_lavador:
    print(f"  - {u.email} ({u.first_name} {u.last_name})")
    try:
        empleado = u.empleado
        print(f"    Empleado: {empleado.nombre} {empleado.apellido}, Cargo: {empleado.cargo.codigo}")
    except Empleado.DoesNotExist:
        print("    Sin registro de empleado asociado")