#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from django.db import connection

def limpiar_tokens_invalidos():
    try:
        with connection.cursor() as cursor:
            # Eliminar registros con tokens inválidos
            cursor.execute("DELETE FROM autenticacion_usuario WHERE verification_token = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'")
            print(f"Registros eliminados: {cursor.rowcount}")
            
            # Verificar cuántos usuarios quedan
            cursor.execute("SELECT COUNT(*) FROM autenticacion_usuario")
            count = cursor.fetchone()[0]
            print(f"Usuarios restantes: {count}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    limpiar_tokens_invalidos()