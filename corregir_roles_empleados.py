#!/usr/bin/env python
"""
Script para corregir los roles de los usuarios empleados
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
    print("=== CORRIGIENDO ROLES DE EMPLEADOS ===")
    
    empleados = Empleado.objects.all()
    empleados_corregidos = 0
    
    for emp in empleados:
        if emp.usuario:
            # Verificar si el rol del usuario no coincide con el rol del empleado
            rol_usuario_correcto = Usuario.ROL_LAVADOR if emp.es_lavador() else Usuario.ROL_CLIENTE
            
            if emp.usuario.rol != rol_usuario_correcto:
                print(f"Corrigiendo usuario de {emp.nombre_completo()}:")
                print(f"  - Rol actual: {emp.usuario.rol}")
                print(f"  - Rol correcto: {rol_usuario_correcto}")
                
                emp.usuario.rol = rol_usuario_correcto
                emp.usuario.save()
                empleados_corregidos += 1
                print(f"  ✓ Rol corregido")
            else:
                print(f"✓ {emp.nombre_completo()} ya tiene el rol correcto: {emp.usuario.rol}")
        else:
            print(f"⚠️ {emp.nombre_completo()} no tiene usuario asociado")
    
    print(f"\n=== RESUMEN ===")
    print(f"Empleados procesados: {empleados.count()}")
    print(f"Roles corregidos: {empleados_corregidos}")
    
    # Verificar el estado final
    print(f"\n=== ESTADO FINAL ===")
    for emp in empleados:
        if emp.usuario:
            print(f"{emp.nombre_completo()}: {emp.usuario.email} (rol: {emp.usuario.rol})")

if __name__ == "__main__":
    main()