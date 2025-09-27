#!/usr/bin/env python
import os
import sys
import django
import requests
from django.test import Client
from django.contrib.auth import authenticate

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from empleados.models import Empleado
from notificaciones.models import Notificacion

def test_api_empleado():
    print("=== PROBANDO API DE NOTIFICACIONES PARA EMPLEADOS ===")
    
    # Buscar un empleado con notificaciones
    empleado = Empleado.objects.filter(
        notificaciones__leida=False
    ).first()
    
    if not empleado:
        print("No se encontró empleado con notificaciones no leídas")
        return
    
    print(f"Empleado encontrado: {empleado.usuario.username}")
    print(f"Email: {empleado.usuario.email}")
    
    # Crear cliente de prueba
    client = Client()
    
    # Hacer login
    login_success = client.login(
        username=empleado.usuario.username, 
        password='123456'  # Asumiendo que esta es la contraseña de prueba
    )
    
    if not login_success:
        print("No se pudo hacer login con el empleado")
        # Intentar con diferentes contraseñas comunes
        passwords = ['password', 'admin', '12345', 'empleado123']
        for pwd in passwords:
            if client.login(username=empleado.usuario.username, password=pwd):
                print(f"Login exitoso con contraseña: {pwd}")
                login_success = True
                break
    
    if not login_success:
        print("No se pudo hacer login. Probando sin autenticación...")
        # Probar la vista directamente
        from notificaciones.views import contador_notificaciones_api
        from django.http import HttpRequest
        
        request = HttpRequest()
        request.user = empleado.usuario
        request.method = 'GET'
        
        response = contador_notificaciones_api(request)
        print(f"Respuesta directa de la API: {response.content.decode()}")
        return
    
    # Probar API de contador
    print("\n--- Probando API de contador ---")
    response = client.get('/notificaciones/api/contador/')
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.get('Content-Type', 'No especificado')}")
    print(f"Respuesta: {response.content.decode()}")
    
    # Probar API de dropdown
    print("\n--- Probando API de dropdown ---")
    response = client.get('/notificaciones/api/dropdown/')
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.get('Content-Type', 'No especificado')}")
    print(f"Respuesta: {response.content.decode()}")
    
    # Verificar notificaciones del empleado directamente
    print(f"\n--- Verificación directa ---")
    notifs_no_leidas = Notificacion.objects.filter(
        empleado=empleado,
        tipo__in=[Notificacion.CALIFICACION_RECIBIDA, Notificacion.SERVICIO_ASIGNADO],
        leida=False
    ).count()
    print(f"Notificaciones no leídas (consulta directa): {notifs_no_leidas}")

if __name__ == "__main__":
    test_api_empleado()