#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from django.db import connection
from autenticacion.models import Usuario
from django.contrib.auth.hashers import make_password

def crear_usuario_test():
    email = 'test@example.com'
    password = 'test123'
    
    try:
        # Verificar si el usuario ya existe
        try:
            usuario = Usuario.objects.get(email=email)
            print(f"Usuario {email} ya existe. Eliminando...")
            usuario.delete()
        except Usuario.DoesNotExist:
            print(f"Usuario {email} no existe. Creando nuevo usuario...")
        
        # Crear usuario usando el manager personalizado
        usuario = Usuario.objects.create_user(
            email=email,
            password=password,
            first_name='Test',
            last_name='User',
            is_staff=True,
            is_superuser=True,
            is_verified=True
        )
        
        print(f"Usuario {email} creado exitosamente!")
        print(f"ID: {usuario.id}")
        print(f"Email: {usuario.email}")
        print(f"Superuser: {usuario.is_superuser}")
        print(f"Staff: {usuario.is_staff}")
        print(f"Verificado: {usuario.is_verified}")
        
        return usuario
        
    except Exception as e:
        print(f"Error al crear usuario: {e}")
        return None

if __name__ == "__main__":
    crear_usuario_test()