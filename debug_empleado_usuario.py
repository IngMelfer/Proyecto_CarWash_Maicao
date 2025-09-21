#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from autenticacion.models import Usuario
from empleados.models import Empleado

def verificar_usuario_empleado():
    print("=== VERIFICACIÓN DE USUARIO Y EMPLEADO ===")
    
    # Buscar usuario por email
    email = 'juansoy@correo.com'
    print(f"\n1. Buscando usuario con email: {email}")
    
    try:
        user = Usuario.objects.filter(email=email).first()
        if user:
            print(f"   ✓ Usuario encontrado:")
            print(f"     - ID: {user.id}")
            print(f"     - Username: {user.username}")
            print(f"     - Email: {user.email}")
            print(f"     - Activo: {user.is_active}")
            print(f"     - Staff: {user.is_staff}")
            
            # Verificar si tiene atributo rol
            if hasattr(user, 'rol'):
                print(f"     - Rol: {user.rol}")
            else:
                print("     - Rol: No definido (atributo no existe)")
            
            # Buscar empleado asociado
            print(f"\n2. Buscando empleado asociado al usuario:")
            empleado = Empleado.objects.filter(usuario=user).first()
            
            if empleado:
                print(f"   ✓ Empleado encontrado:")
                print(f"     - ID: {empleado.id}")
                print(f"     - Nombre: {empleado.nombre_completo}")
                print(f"     - Documento: {empleado.documento}")
                print(f"     - Cargo: {empleado.cargo}")
                print(f"     - Activo: {empleado.activo}")
            else:
                print("   ✗ No se encontró empleado asociado")
                
                # Buscar empleados con documento similar
                print(f"\n3. Buscando empleados por documento:")
                empleados_doc = Empleado.objects.filter(documento__icontains=user.username)
                if empleados_doc.exists():
                    for emp in empleados_doc:
                        print(f"     - Empleado ID {emp.id}: {emp.nombre_completo} (Doc: {emp.documento})")
                        print(f"       Usuario asociado: {emp.usuario}")
                else:
                    print("     No se encontraron empleados con documento similar")
        else:
            print(f"   ✗ Usuario no encontrado con email: {email}")
            
            # Buscar por username
            print(f"\n   Buscando por username que contenga 'juansoy':")
            users = Usuario.objects.filter(username__icontains='juansoy')
            for u in users:
                print(f"     - Usuario: {u.username} (Email: {u.email})")
    
    except Exception as e:
        print(f"Error al verificar usuario: {e}")
    
    # Estadísticas generales
    print(f"\n=== ESTADÍSTICAS GENERALES ===")
    print(f"Total usuarios: {Usuario.objects.count()}")
    print(f"Total empleados: {Empleado.objects.count()}")
    print(f"Empleados sin usuario: {Empleado.objects.filter(usuario__isnull=True).count()}")
    print(f"Usuarios sin empleado: {Usuario.objects.filter(empleado__isnull=True).count()}")
    
    # Verificar usuarios con rol Lavador
    print(f"\n=== USUARIOS CON ROL LAVADOR ===")
    try:
        lavadores = Usuario.objects.filter(rol='lavador')
        print(f"Total usuarios con rol 'lavador': {lavadores.count()}")
        for lavador in lavadores:
            print(f"  - {lavador.username} ({lavador.email}) - Activo: {lavador.is_active}")
            empleado_asociado = Empleado.objects.filter(usuario=lavador).first()
            if empleado_asociado:
                print(f"    ✓ Empleado asociado: {empleado_asociado.nombre_completo}")
            else:
                print(f"    ✗ Sin empleado asociado")
    except Exception as e:
        print(f"Error al verificar usuarios con rol lavador: {e}")

if __name__ == "__main__":
    verificar_usuario_empleado()