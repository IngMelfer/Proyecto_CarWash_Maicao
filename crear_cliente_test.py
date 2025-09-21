#!/usr/bin/env python
"""
Script para crear un perfil de cliente para el usuario actual de testing
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from django.contrib.auth import get_user_model
from clientes.models import Cliente

User = get_user_model()

def crear_cliente_test():
    """Crear un perfil de cliente para el usuario actual"""
    try:
        # Obtener el primer usuario disponible (para testing)
        usuario = User.objects.first()
        if not usuario:
            print("No hay usuarios en el sistema")
            return
        
        print(f"Usuario encontrado: {usuario.email}")
        
        # Verificar si ya tiene un cliente asociado
        try:
            cliente_existente = usuario.cliente
            print(f"El usuario ya tiene un perfil de cliente: {cliente_existente}")
            return cliente_existente
        except Cliente.DoesNotExist:
            pass
        
        # Crear el perfil de cliente
        cliente = Cliente.objects.create(
            usuario=usuario,
            nombre=usuario.first_name or "Usuario",
            apellido=usuario.last_name or "Test",
            email=usuario.email,
            tipo_documento=Cliente.CEDULA,
            numero_documento="12345678",
            telefono="3001234567",
            direccion="Calle Test 123",
            ciudad="Maicao"
        )
        
        print(f"Cliente creado exitosamente: {cliente}")
        return cliente
        
    except Exception as e:
        print(f"Error al crear cliente: {e}")
        return None

if __name__ == "__main__":
    crear_cliente_test()