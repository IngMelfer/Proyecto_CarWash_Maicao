#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from autenticacion.models import Usuario

def check_user_role():
    try:
        user = Usuario.objects.filter(email='test1@example.com').first()
        if user:
            print(f"Usuario encontrado: {user.email}")
            print(f"Rol: {user.rol}")
            print(f"Rol Display: {user.get_rol_display()}")
            print(f"Is Staff: {user.is_staff}")
            print(f"Is Superuser: {user.is_superuser}")
            
            # Verificar si es ADMIN_SISTEMA
            if user.rol == Usuario.ROL_ADMIN_SISTEMA:
                print("✅ El usuario ES un Administrador del Sistema")
            else:
                print("❌ El usuario NO es un Administrador del Sistema")
                
        else:
            print("❌ Usuario test1@example.com no encontrado")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_user_role()