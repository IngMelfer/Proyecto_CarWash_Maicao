#!/usr/bin/env python
"""
Script para probar múltiples endpoints de la API REST
"""
import os
import sys
import django
import requests
import json
from bs4 import BeautifulSoup
import re

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
os.environ['ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver'
django.setup()

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/autenticacion/login/"
CSRF_URL = f"{BASE_URL}/autenticacion/login/"

# Credenciales del usuario de prueba
EMAIL = "test@example.com"
PASSWORD = "test123"

def obtener_csrf_token(session):
    """Obtiene el token CSRF de la página de login"""
    print("1. Obteniendo token CSRF...")
    response = session.get(CSRF_URL)
    print(f"Status CSRF: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Error obteniendo CSRF: {response.status_code}")
        return None
    
    # Buscar token en cookies
    csrf_token = session.cookies.get('csrftoken')
    if csrf_token:
        print(f"Token CSRF obtenido: {csrf_token[:10]}...")
        return csrf_token
    
    # Si no está en cookies, buscar en el HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if csrf_input:
        csrf_token = csrf_input.get('value')
        print(f"Token CSRF obtenido del HTML: {csrf_token[:10]}...")
        return csrf_token
    
    print("❌ No se pudo obtener el token CSRF")
    return None

def hacer_login(session, csrf_token):
    """Realiza el login con las credenciales"""
    print("2. Haciendo login...")
    
    login_data = {
        'email': EMAIL,
        'password': PASSWORD,
        'csrfmiddlewaretoken': csrf_token
    }
    
    headers = {
        'X-CSRFToken': csrf_token,
        'Referer': LOGIN_URL
    }
    
    response = session.post(LOGIN_URL, data=login_data, headers=headers, allow_redirects=True)
    print(f"Status login: {response.status_code}")
    print(f"URL final después del login: {response.url}")
    
    # Considerar login exitoso si no estamos en la página de login
    if response.status_code == 200 and 'login' not in response.url:
        print("✅ Login exitoso!")
        return True
    else:
        print("❌ Error en login")
        return False

def probar_endpoint(session, csrf_token, endpoint_name, url, method='GET', data=None):
    """Prueba un endpoint específico de la API"""
    print(f"\n--- Probando {endpoint_name} ---")
    print(f"URL: {url}")
    print(f"Método: {method}")
    
    headers = {
        'X-CSRFToken': csrf_token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        if method.upper() == 'GET':
            response = session.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = session.post(url, json=data, headers=headers)
        else:
            print(f"❌ Método {method} no soportado")
            return False
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Respuesta JSON válida")
                
                # Mostrar información relevante según el tipo de respuesta
                if isinstance(data, dict):
                    if 'count' in data and 'results' in data:
                        print(f"📊 Paginación: {data['count']} elementos totales")
                        print(f"📋 Elementos en esta página: {len(data['results'])}")
                        if data['results']:
                            print(f"🔍 Primer elemento: {json.dumps(data['results'][0], indent=2, ensure_ascii=False)[:200]}...")
                    else:
                        print(f"📄 Datos: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}...")
                elif isinstance(data, list):
                    print(f"📋 Lista con {len(data)} elementos")
                    if data:
                        print(f"🔍 Primer elemento: {json.dumps(data[0], indent=2, ensure_ascii=False)[:200]}...")
                
                return True
            except json.JSONDecodeError:
                print("❌ Respuesta no es JSON válido")
                print(f"Contenido: {response.text[:300]}...")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Contenido: {response.text[:300]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

from autenticacion.models import Usuario

def main():
    print("=== PRUEBA COMPLETA DE API REST ===\n")
    
    # Crear sesión
    session = requests.Session()
    
    # Asegurar usuario de prueba
    try:
        usuario, created = Usuario.objects.get_or_create(
            email=EMAIL,
            defaults={
                'first_name': 'Test',
                'last_name': 'API',
                'rol': Usuario.ROL_CLIENTE,
                'is_active': True,
                'is_verified': True,
            }
        )
        # Asegurar verificación y contraseña conocida
        usuario.is_verified = True
        usuario.set_password(PASSWORD)
        usuario.save()
        print(f"Usuario de prueba {'creado' if created else 'actualizado'}: {EMAIL}")
    except Exception as e:
        print(f"❌ No se pudo crear/actualizar el usuario de prueba: {e}")
        return False
    
    # Obtener token CSRF
    csrf_token = obtener_csrf_token(session)
    if not csrf_token:
        print("💥 No se pudo obtener el token CSRF")
        return False
    
    # Hacer login
    if not hacer_login(session, csrf_token):
        print("💥 Error en el login")
        return False
    
    # Lista de endpoints para probar
    endpoints = [
        {
            'name': 'Servicios',
            'url': f'{BASE_URL}/api/reservas/servicios/',
            'method': 'GET'
        },
        {
            'name': 'Reservas',
            'url': f'{BASE_URL}/api/reservas/reservas/',
            'method': 'GET'
        },
        {
            'name': 'Bahías',
            'url': f'{BASE_URL}/api/reservas/bahias/',
            'method': 'GET'
        },
        {
            'name': 'Clientes',
            'url': f'{BASE_URL}/api/clientes/clientes/',
            'method': 'GET'
        },
        {
            'name': 'Historial de Servicios',
            'url': f'{BASE_URL}/api/clientes/historial/',
            'method': 'GET'
        },
        {
            'name': 'Perfil de Usuario (API Auth)',
            'url': f'{BASE_URL}/api/auth/api/perfil/',
            'method': 'GET'
        }
    ]
    
    # Probar cada endpoint
    resultados = {}
    for endpoint in endpoints:
        resultado = probar_endpoint(
            session, 
            csrf_token, 
            endpoint['name'], 
            endpoint['url'], 
            endpoint['method']
        )
        resultados[endpoint['name']] = resultado
    
    # Resumen final
    print("\n" + "="*50)
    print("RESUMEN DE PRUEBAS")
    print("="*50)
    
    exitosos = 0
    for nombre, resultado in resultados.items():
        estado = "✅ EXITOSO" if resultado else "❌ FALLÓ"
        print(f"{nombre}: {estado}")
        if resultado:
            exitosos += 1
    
    print(f"\nTotal: {exitosos}/{len(resultados)} endpoints funcionando correctamente")
    
    if exitosos == len(resultados):
        print("\n🎉 ¡Todas las pruebas de API fueron exitosas!")
        return True
    else:
        print(f"\n⚠️  {len(resultados) - exitosos} endpoints fallaron")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)