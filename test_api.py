#!/usr/bin/env python
"""
Script para probar los endpoints de la API REST
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

import requests
import json
from django.contrib.auth import get_user_model
from reservas.models import Servicio, Bahia
from autenticacion.models import Usuario

def test_api_endpoints():
    """Probar los endpoints principales de la API"""
    
    print("=== PRUEBA DE API REST ===\n")
    
    # Crear datos de prueba
    print("1. Creando datos de prueba...")
    
    # Crear servicio
    servicio, created = Servicio.objects.get_or_create(
        nombre='Lavado Básico API Test',
        defaults={
            'descripcion': 'Servicio de prueba para API',
            'precio': 15000,
            'duracion_minutos': 30,
            'activo': True
        }
    )
    print(f"   Servicio: {servicio} ({'creado' if created else 'existente'})")
    
    # Crear bahía
    bahia, created = Bahia.objects.get_or_create(
        nombre='Bahía API Test',
        defaults={
            'descripcion': 'Bahía de prueba para API',
            'activo': True,
            'tiene_camara': False
        }
    )
    print(f"   Bahía: {bahia} ({'creada' if created else 'existente'})")
    
    # Crear usuario
    usuario, created = Usuario.objects.get_or_create(
        email='test@api.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'API',
            'is_active': True
        }
    )
    if created:
        usuario.set_password('testpass123')
        usuario.save()
    print(f"   Usuario: {usuario} ({'creado' if created else 'existente'})")
    
    print("\n2. Probando endpoints de la API...")
    
    base_url = 'http://127.0.0.1:8000/api'
    
    # Lista de endpoints a probar
    endpoints = [
        '/servicios/',
        '/bahias/',
        '/reservas/',
    ]
    
    for endpoint in endpoints:
        url = base_url + endpoint
        try:
            print(f"   Probando: {url}")
            response = requests.get(url, timeout=5)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   Resultados: {len(data)} elementos")
                    elif isinstance(data, dict):
                        print(f"   Respuesta: {list(data.keys())}")
                except json.JSONDecodeError:
                    print(f"   Respuesta no es JSON válido")
            else:
                print(f"   Error: {response.text[:100]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"   ERROR: No se puede conectar al servidor en {url}")
            print("   Asegúrate de que el servidor esté corriendo con: python manage.py runserver")
        except requests.exceptions.RequestException as e:
            print(f"   ERROR: {e}")
        
        print()
    
    print("=== FIN DE PRUEBA DE API ===")

if __name__ == '__main__':
    test_api_endpoints()