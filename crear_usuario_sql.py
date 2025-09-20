#!/usr/bin/env python
import os
import sys
import django
import uuid

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from django.db import connection
from django.contrib.auth.hashers import make_password

def crear_usuario_sql():
    email = 'test@example.com'
    password = 'test123'
    
    try:
        with connection.cursor() as cursor:
            # Eliminar usuario si existe
            cursor.execute("DELETE FROM autenticacion_usuario WHERE email = %s", [email])
            print(f"Usuario {email} eliminado si existía")
            
            # Crear contraseña hasheada
            hashed_password = make_password(password)
            
            # Generar UUID válido de 32 caracteres sin guiones
            verification_token = str(uuid.uuid4()).replace('-', '')
            
            # Crear usuario con SQL directo
            cursor.execute("""
                INSERT INTO autenticacion_usuario 
                (password, last_login, is_superuser, first_name, last_name, is_staff, is_active, date_joined, email, is_verified, verification_token, token_created_at, foto_perfil, rol)
                VALUES 
                (%s, NULL, 1, 'Test', 'User', 1, 1, NOW(), %s, 1, %s, NOW(), NULL, 'admin')
            """, [hashed_password, email, verification_token])
            
            print(f"Usuario {email} creado exitosamente!")
            
            # Verificar el usuario creado
            cursor.execute("SELECT id, email, is_superuser, is_staff, is_verified, rol FROM autenticacion_usuario WHERE email = %s", [email])
            user_data = cursor.fetchone()
            
            if user_data:
                print(f"ID: {user_data[0]}")
                print(f"Email: {user_data[1]}")
                print(f"Superuser: {user_data[2]}")
                print(f"Staff: {user_data[3]}")
                print(f"Verificado: {user_data[4]}")
                print(f"Rol: {user_data[5]}")
                print(f"Contraseña: {password}")
                return True
            else:
                print("Error: No se pudo verificar el usuario creado")
                return False
                
    except Exception as e:
        print(f"Error al crear usuario: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    crear_usuario_sql()