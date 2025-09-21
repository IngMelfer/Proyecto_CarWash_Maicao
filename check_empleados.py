#!/usr/bin/env python
"""
Script para verificar el estado actual de los empleados en la base de datos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from empleados.models import Empleado
from autenticacion.models import Usuario

def main():
    print("=== EMPLEADOS EN LA BASE DE DATOS ===")
    
    empleados = Empleado.objects.all()
    print(f"Total empleados: {empleados.count()}")
    print()
    
    empleados_sin_usuario = []
    
    for emp in empleados:
        try:
            if emp.usuario:
                usuario_info = f"Usuario: {emp.usuario.email}, Activo: {emp.usuario.is_active}"
            else:
                usuario_info = "SIN USUARIO ASOCIADO"
                empleados_sin_usuario.append(emp)
        except Exception as e:
            usuario_info = f"ERROR AL ACCEDER AL USUARIO: {str(e)}"
            empleados_sin_usuario.append(emp)
            
        print(f"ID: {emp.id}")
        print(f"Nombre: {emp.nombre_completo()}")
        print(f"Documento: {emp.numero_documento}")
        print(f"Cargo: {emp.cargo.nombre}")
        print(f"Rol: {emp.rol}")
        print(f"{usuario_info}")
        print("-" * 50)
    
    print(f"\n=== USUARIOS EN EL SISTEMA ===")
    usuarios = Usuario.objects.all()
    print(f"Total usuarios: {usuarios.count()}")
    for usuario in usuarios:
        print(f"Email: {usuario.email}, Rol: {usuario.rol}, Activo: {usuario.is_active}")
    
    print(f"\n=== RESUMEN ===")
    print(f"Total empleados: {empleados.count()}")
    print(f"Empleados sin usuario: {len(empleados_sin_usuario)}")
    print(f"Total usuarios en el sistema: {usuarios.count()}")
    
    if empleados_sin_usuario:
        print("\nEmpleados que necesitan usuario:")
        for emp in empleados_sin_usuario:
            print(f"- {emp.nombre_completo()} (Doc: {emp.numero_documento})")

if __name__ == "__main__":
    main()