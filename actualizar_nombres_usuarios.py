#!/usr/bin/env python
"""
Script para actualizar los campos first_name y last_name de usuarios existentes
basándose en los datos del modelo Cliente asociado.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from autenticacion.models import Usuario
from clientes.models import Cliente

def actualizar_nombres_usuarios():
    """Actualiza los nombres de usuarios basándose en los datos del cliente"""
    usuarios_actualizados = 0
    usuarios_sin_cliente = 0
    
    print("Iniciando actualización de nombres de usuarios...")
    
    # Obtener todos los usuarios
    usuarios = Usuario.objects.all()
    
    for usuario in usuarios:
        try:
            # Buscar el cliente asociado
            cliente = Cliente.objects.get(usuario=usuario)
            
            # Verificar si necesita actualización
            if not usuario.first_name or not usuario.last_name:
                usuario.first_name = cliente.nombre or ''
                usuario.last_name = cliente.apellido or ''
                usuario.save()
                usuarios_actualizados += 1
                print(f"✓ Actualizado: {usuario.email} -> {usuario.get_full_name()}")
            else:
                print(f"- Ya tiene nombres: {usuario.email} -> {usuario.get_full_name()}")
                
        except Cliente.DoesNotExist:
            usuarios_sin_cliente += 1
            print(f"⚠ Usuario sin cliente asociado: {usuario.email}")
    
    print(f"\n=== RESUMEN ===")
    print(f"Usuarios actualizados: {usuarios_actualizados}")
    print(f"Usuarios sin cliente: {usuarios_sin_cliente}")
    print(f"Total usuarios procesados: {len(usuarios)}")

if __name__ == "__main__":
    actualizar_nombres_usuarios()