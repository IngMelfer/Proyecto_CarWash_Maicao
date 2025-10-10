import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
os.environ['ALLOWED_HOSTS'] = 'localhost,127.0.0.1,testserver'
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

print('PRUEBAS DE INTERFAZ DE USUARIO Y RESPONSIVIDAD')
print('=' * 60)

client = Client()

# Páginas principales a probar
urls_to_test = [
    ('/', 'Página principal'),
    ('/autenticacion/login/', 'Página de login'),
    ('/autenticacion/registro/', 'Página de registro'),
    ('/reservas/reservar_turno/', 'Página de reservar turno'),
]

print('Probando accesibilidad de páginas principales:')
for url, description in urls_to_test:
    try:
        response = client.get(url)
        status = 'OK' if response.status_code in [200, 302] else 'ERROR'
        print(f'   {status} {description}: {response.status_code}')
        
        # Verificar contenido HTML básico
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            has_viewport = 'viewport' in content
            has_bootstrap = 'bootstrap' in content.lower()
            has_responsive = 'responsive' in content.lower() or 'col-' in content
            
            print(f'      - Viewport meta tag: {"SI" if has_viewport else "NO"}')
            print(f'      - Bootstrap/CSS framework: {"SI" if has_bootstrap else "NO"}')
            print(f'      - Clases responsivas: {"SI" if has_responsive else "NO"}')
            
    except Exception as e:
        print(f'   ERROR {description}: {str(e)}')

print('\nVerificando archivos estáticos:')
static_files = [
    'static/css/',
    'static/js/',
    'static/img/',
]

for static_dir in static_files:
    if os.path.exists(static_dir):
        files = os.listdir(static_dir)
        print(f'   OK {static_dir}: {len(files)} archivos')
    else:
        print(f'   ERROR {static_dir}: No encontrado')

print('\nVerificando templates:')
template_dirs = [
    'templates/',
    'templates/autenticacion/',
    'templates/reservas/',
    'templates/empleados/',
    'templates/clientes/',
]

for template_dir in template_dirs:
    if os.path.exists(template_dir):
        files = [f for f in os.listdir(template_dir) if f.endswith('.html')]
        print(f'   OK {template_dir}: {len(files)} templates HTML')
    else:
        print(f'   ERROR {template_dir}: No encontrado')

print('\nPRUEBAS DE INTERFAZ COMPLETADAS')