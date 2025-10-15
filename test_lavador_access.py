#!/usr/bin/env python
import os
import django
import requests
from django.test import Client
from django.contrib.auth import authenticate

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from autenticacion.models import Usuario
from empleados.models import Empleado

def test_lavador_access():
    print("=== Test de acceso para usuarios lavador ===\n")
    
    # Buscar usuarios con rol lavador
    usuarios_lavador = Usuario.objects.filter(rol='lavador')
    print(f'Usuarios con rol lavador encontrados: {usuarios_lavador.count()}')
    
    for usuario in usuarios_lavador:
        print(f'- {usuario.email} (verificado: {usuario.is_verified})')
        
        # Verificar si tiene empleado asociado
        try:
            empleado = Empleado.objects.get(usuario=usuario)
            cargo_info = empleado.cargo.nombre if empleado.cargo else "Sin cargo"
            cargo_codigo = empleado.cargo.codigo if empleado.cargo else "Sin código"
            print(f'  Empleado: {empleado.nombre} {empleado.apellido}')
            print(f'  Cargo: {cargo_info} (código: {cargo_codigo})')
        except Empleado.DoesNotExist:
            print(f'  Sin empleado asociado')
        
        # Test de autenticación
        if usuario.is_verified:
            print(f'  Probando acceso a página de bonificaciones...')
            
            # Crear cliente de test
            client = Client()
            
            # Intentar login
            login_success = client.login(username=usuario.email, password='123456')  # Contraseña común de test
            if not login_success:
                # Probar con otras contraseñas comunes
                for pwd in ['password', 'admin', '12345', 'test123']:
                    login_success = client.login(username=usuario.email, password=pwd)
                    if login_success:
                        print(f'  Login exitoso con contraseña: {pwd}')
                        break
            
            if login_success:
                # Probar acceso a la página de bonificaciones
                response = client.get('/empleados/bonificaciones-v2/')
                print(f'  Respuesta de bonificaciones: {response.status_code}')
                
                if response.status_code == 200:
                    content = response.content.decode('utf-8')
                    if 'login' in content.lower() or 'iniciar sesión' in content.lower():
                        print(f'  ❌ Página muestra formulario de login (no autenticado)')
                    elif 'bonificaciones' in content.lower() or 'puntos' in content.lower():
                        print(f'  ✅ Página muestra contenido de bonificaciones')
                    else:
                        print(f'  ⚠️  Contenido no identificado')
                elif response.status_code == 302:
                    print(f'  ↩️  Redirección a: {response.get("Location", "desconocido")}')
                else:
                    print(f'  ❌ Error: {response.status_code}')
            else:
                print(f'  ❌ No se pudo hacer login')
        else:
            print(f'  ⚠️  Usuario no verificado')
        
        print()

if __name__ == '__main__':
    test_lavador_access()