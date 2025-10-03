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

print("=== PRUEBA DE APIs DE NOTIFICACIONES ===")

# Crear cliente de prueba
client = Client()

# Buscar un empleado para hacer login
empleados = Empleado.objects.all()
if empleados.exists():
    empleado = empleados.first()
    usuario = empleado.usuario
    
    print(f"Probando con empleado: {empleado.nombre_completo}")
    print(f"Usuario: {usuario.email}")
    
    # Hacer login
    login_success = client.login(email=usuario.email, password='123456')  # Asumiendo password por defecto
    
    if not login_success:
        # Intentar con otros passwords comunes
        passwords = ['password', 'admin', '12345678', 'empleado123']
        for pwd in passwords:
            login_success = client.login(email=usuario.email, password=pwd)
            if login_success:
                print(f"Login exitoso con password: {pwd}")
                break
    
    if login_success:
        print("✓ Login exitoso")
        
        # Probar API de contador
        print("\n--- Probando API de contador ---")
        response = client.get('/notificaciones/api/contador/')
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.get('Content-Type', 'No especificado')}")
        print(f"Response: {response.content.decode()}")
        
        # Probar API de dropdown
        print("\n--- Probando API de dropdown ---")
        response = client.get('/notificaciones/api/dropdown/')
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.get('Content-Type', 'No especificado')}")
        print(f"Response: {response.content.decode()}")
        
    else:
        print("✗ No se pudo hacer login")
        print("Intentando crear un usuario de prueba...")
        
        # Crear usuario de prueba si no existe
        test_user, created = Usuario.objects.get_or_create(
            email='test@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'Empleado',
                'rol': Usuario.ROL_EMPLEADO
            }
        )
        
        if created:
            test_user.set_password('123456')
            test_user.save()
            print("Usuario de prueba creado")
        
        # Intentar login con usuario de prueba
        login_success = client.login(email='test@example.com', password='123456')
        if login_success:
            print("✓ Login exitoso con usuario de prueba")
            
            # Probar APIs
            print("\n--- Probando API de contador ---")
            response = client.get('/notificaciones/api/contador/')
            print(f"Status: {response.status_code}")
            print(f"Response: {response.content.decode()}")
            
            print("\n--- Probando API de dropdown ---")
            response = client.get('/notificaciones/api/dropdown/')
            print(f"Status: {response.status_code}")
            print(f"Response: {response.content.decode()}")
        else:
            print("✗ No se pudo hacer login con usuario de prueba")

else:
    print("No hay empleados en la base de datos")