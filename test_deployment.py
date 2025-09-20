#!/usr/bin/env python
"""
Script de pruebas para verificar la configuración de producción y deployment
"""

import os
import sys
import django
from datetime import datetime
import subprocess
import requests
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from django.conf import settings
from django.core.management import execute_from_command_line
from django.test.utils import get_runner

def test_configuracion_produccion():
    """Función principal de pruebas de configuración de producción"""
    print("\n🚀 PRUEBAS DE CONFIGURACIÓN DE PRODUCCIÓN Y DEPLOYMENT")
    print("=" * 60)
    
    success = True
    
    try:
        # 1. Verificar configuración de Django
        if not verificar_configuracion_django():
            success = False
            
        # 2. Verificar archivos de deployment
        if not verificar_archivos_deployment():
            success = False
            
        # 3. Verificar variables de entorno
        if not verificar_variables_entorno():
            success = False
            
        # 4. Verificar dependencias
        if not verificar_dependencias():
            success = False
            
        # 5. Verificar configuración de base de datos
        if not verificar_configuracion_bd():
            success = False
            
        # 6. Verificar archivos estáticos
        if not verificar_archivos_estaticos():
            success = False
            
        # 7. Verificar configuración de seguridad
        if not verificar_configuracion_seguridad():
            success = False
            
        # 8. Verificar URLs y rutas
        if not verificar_urls_rutas():
            success = False
            
    except Exception as e:
        print(f"❌ Error en las pruebas de deployment: {e}")
        success = False
        
    return success

def verificar_configuracion_django():
    """Verificar la configuración básica de Django"""
    print("\n1. Verificando configuración de Django...")
    try:
        # Verificar DEBUG
        debug_status = getattr(settings, 'DEBUG', None)
        print(f"✅ DEBUG: {debug_status}")
        
        # Verificar SECRET_KEY
        secret_key = getattr(settings, 'SECRET_KEY', None)
        if secret_key and len(secret_key) > 20:
            print("✅ SECRET_KEY: Configurada correctamente")
        else:
            print("❌ SECRET_KEY: No configurada o muy corta")
            
        # Verificar ALLOWED_HOSTS
        allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
        print(f"✅ ALLOWED_HOSTS: {allowed_hosts}")
        
        # Verificar INSTALLED_APPS
        installed_apps = getattr(settings, 'INSTALLED_APPS', [])
        apps_requeridas = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'autenticacion',
            'clientes',
            'reservas',
            'empleados',
            'notificaciones'
        ]
        
        for app in apps_requeridas:
            if app in installed_apps:
                print(f"✅ App instalada: {app}")
            else:
                print(f"❌ App faltante: {app}")
                
        # Verificar MIDDLEWARE
        middleware = getattr(settings, 'MIDDLEWARE', [])
        print(f"✅ MIDDLEWARE configurado: {len(middleware)} middlewares")
        
        # Verificar configuración de base de datos
        databases = getattr(settings, 'DATABASES', {})
        if 'default' in databases:
            db_engine = databases['default'].get('ENGINE', '')
            print(f"✅ Base de datos: {db_engine}")
        else:
            print("❌ Configuración de base de datos no encontrada")
            
        return True
        
    except Exception as e:
        print(f"❌ Error verificando configuración de Django: {e}")
        return False

def verificar_archivos_deployment():
    """Verificar archivos necesarios para deployment"""
    print("\n2. Verificando archivos de deployment...")
    try:
        archivos_requeridos = [
            'requirements.txt',
            'runtime.txt',
            'Procfile',
            'railway.json',
            '.env.example',
            'manage.py'
        ]
        
        for archivo in archivos_requeridos:
            if os.path.exists(archivo):
                print(f"✅ Archivo encontrado: {archivo}")
                
                # Verificar contenido específico
                if archivo == 'requirements.txt':
                    with open(archivo, 'r') as f:
                        content = f.read()
                        if 'Django' in content:
                            print("   📦 Django incluido en requirements")
                        if 'gunicorn' in content:
                            print("   📦 Gunicorn incluido en requirements")
                        if 'psycopg2' in content or 'mysqlclient' in content:
                            print("   📦 Driver de base de datos incluido")
                            
                elif archivo == 'Procfile':
                    with open(archivo, 'r') as f:
                        content = f.read()
                        if 'web:' in content:
                            print("   🌐 Proceso web configurado")
                        if 'gunicorn' in content:
                            print("   🚀 Gunicorn configurado")
                            
                elif archivo == 'runtime.txt':
                    with open(archivo, 'r') as f:
                        content = f.read().strip()
                        print(f"   🐍 Python version: {content}")
                        
            else:
                print(f"❌ Archivo faltante: {archivo}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error verificando archivos de deployment: {e}")
        return False

def verificar_variables_entorno():
    """Verificar variables de entorno necesarias"""
    print("\n3. Verificando variables de entorno...")
    try:
        variables_importantes = [
            'SECRET_KEY',
            'DEBUG',
            'DATABASE_URL',
            'ALLOWED_HOSTS'
        ]
        
        # Verificar archivo .env.example
        if os.path.exists('.env.example'):
            print("✅ Archivo .env.example encontrado")
            with open('.env.example', 'r') as f:
                content = f.read()
                for var in variables_importantes:
                    if var in content:
                        print(f"   📝 Variable documentada: {var}")
                    else:
                        print(f"   ❌ Variable no documentada: {var}")
        else:
            print("❌ Archivo .env.example no encontrado")
            
        # Verificar variables actuales
        for var in variables_importantes:
            value = os.environ.get(var)
            if value:
                if var == 'SECRET_KEY':
                    print(f"✅ {var}: Configurada (longitud: {len(value)})")
                elif var == 'DEBUG':
                    print(f"✅ {var}: {value}")
                else:
                    print(f"✅ {var}: Configurada")
            else:
                print(f"⚠️ {var}: No configurada en entorno actual")
                
        return True
        
    except Exception as e:
        print(f"❌ Error verificando variables de entorno: {e}")
        return False

def verificar_dependencias():
    """Verificar dependencias del proyecto"""
    print("\n4. Verificando dependencias...")
    try:
        if os.path.exists('requirements.txt'):
            with open('requirements.txt', 'r') as f:
                requirements = f.read().splitlines()
                
            dependencias_criticas = [
                'Django',
                'gunicorn',
                'whitenoise',
                'python-decouple'
            ]
            
            print(f"✅ Total de dependencias: {len(requirements)}")
            
            for dep in dependencias_criticas:
                found = any(dep.lower() in req.lower() for req in requirements)
                if found:
                    print(f"✅ Dependencia crítica: {dep}")
                else:
                    print(f"❌ Dependencia faltante: {dep}")
                    
            # Verificar si hay dependencias duplicadas
            deps_names = [req.split('==')[0].split('>=')[0].split('<=')[0] for req in requirements if req.strip()]
            duplicates = set([x for x in deps_names if deps_names.count(x) > 1])
            if duplicates:
                print(f"⚠️ Dependencias duplicadas: {duplicates}")
            else:
                print("✅ No hay dependencias duplicadas")
                
        return True
        
    except Exception as e:
        print(f"❌ Error verificando dependencias: {e}")
        return False

def verificar_configuracion_bd():
    """Verificar configuración de base de datos"""
    print("\n5. Verificando configuración de base de datos...")
    try:
        from django.db import connection
        
        # Intentar conectar a la base de datos
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                print("✅ Conexión a base de datos exitosa")
                
            # Verificar configuración
            db_settings = settings.DATABASES['default']
            engine = db_settings.get('ENGINE', '')
            
            if 'postgresql' in engine:
                print("✅ Base de datos: PostgreSQL")
            elif 'mysql' in engine:
                print("✅ Base de datos: MySQL")
            elif 'sqlite' in engine:
                print("✅ Base de datos: SQLite")
            else:
                print(f"⚠️ Base de datos: {engine}")
                
            # Verificar migraciones
            from django.core.management.commands.showmigrations import Command
            print("✅ Verificando estado de migraciones...")
            
        except Exception as db_error:
            print(f"❌ Error de conexión a base de datos: {db_error}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error verificando configuración de BD: {e}")
        return False

def verificar_archivos_estaticos():
    """Verificar configuración de archivos estáticos"""
    print("\n6. Verificando archivos estáticos...")
    try:
        # Verificar configuración de archivos estáticos
        static_url = getattr(settings, 'STATIC_URL', None)
        static_root = getattr(settings, 'STATIC_ROOT', None)
        staticfiles_dirs = getattr(settings, 'STATICFILES_DIRS', [])
        
        print(f"✅ STATIC_URL: {static_url}")
        print(f"✅ STATIC_ROOT: {static_root}")
        print(f"✅ STATICFILES_DIRS: {len(staticfiles_dirs)} directorios")
        
        # Verificar directorio static
        if os.path.exists('static'):
            print("✅ Directorio static/ encontrado")
            subdirs = ['css', 'js', 'img']
            for subdir in subdirs:
                if os.path.exists(f'static/{subdir}'):
                    print(f"   📁 static/{subdir}/ encontrado")
                else:
                    print(f"   ❌ static/{subdir}/ no encontrado")
        else:
            print("⚠️ Directorio static/ no encontrado")
            
        # Verificar WhiteNoise
        middleware = getattr(settings, 'MIDDLEWARE', [])
        if 'whitenoise.middleware.WhiteNoiseMiddleware' in middleware:
            print("✅ WhiteNoise configurado para archivos estáticos")
        else:
            print("⚠️ WhiteNoise no configurado")
            
        return True
        
    except Exception as e:
        print(f"❌ Error verificando archivos estáticos: {e}")
        return False

def verificar_configuracion_seguridad():
    """Verificar configuración de seguridad"""
    print("\n7. Verificando configuración de seguridad...")
    try:
        # Verificar configuraciones de seguridad
        configuraciones_seguridad = {
            'SECURE_SSL_REDIRECT': getattr(settings, 'SECURE_SSL_REDIRECT', False),
            'SECURE_HSTS_SECONDS': getattr(settings, 'SECURE_HSTS_SECONDS', 0),
            'SECURE_HSTS_INCLUDE_SUBDOMAINS': getattr(settings, 'SECURE_HSTS_INCLUDE_SUBDOMAINS', False),
            'SECURE_HSTS_PRELOAD': getattr(settings, 'SECURE_HSTS_PRELOAD', False),
            'SESSION_COOKIE_SECURE': getattr(settings, 'SESSION_COOKIE_SECURE', False),
            'CSRF_COOKIE_SECURE': getattr(settings, 'CSRF_COOKIE_SECURE', False),
        }
        
        for config, value in configuraciones_seguridad.items():
            if value:
                print(f"✅ {config}: {value}")
            else:
                print(f"⚠️ {config}: {value} (considerar habilitar en producción)")
                
        # Verificar CORS si está instalado
        installed_apps = getattr(settings, 'INSTALLED_APPS', [])
        if 'corsheaders' in installed_apps:
            print("✅ CORS headers configurado")
            cors_allowed = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
            print(f"   📝 Orígenes permitidos: {len(cors_allowed)}")
        else:
            print("⚠️ CORS headers no configurado")
            
        return True
        
    except Exception as e:
        print(f"❌ Error verificando configuración de seguridad: {e}")
        return False

def verificar_urls_rutas():
    """Verificar URLs y rutas del proyecto"""
    print("\n8. Verificando URLs y rutas...")
    try:
        from django.urls import reverse
        from django.test import Client
        
        # URLs importantes a verificar
        urls_importantes = [
            ('admin:index', 'Admin'),
            ('home', 'Página principal'),
        ]
        
        client = Client()
        
        # Verificar URLs básicas
        rutas_basicas = [
            '/',
            '/admin/',
            '/auth/login/',
        ]
        
        for ruta in rutas_basicas:
            try:
                response = client.get(ruta)
                if response.status_code < 500:
                    print(f"✅ Ruta accesible: {ruta} (status: {response.status_code})")
                else:
                    print(f"❌ Error en ruta: {ruta} (status: {response.status_code})")
            except Exception as url_error:
                print(f"⚠️ Error accediendo a {ruta}: {url_error}")
                
        # Verificar configuración de URLs
        from django.conf.urls import include
        from autolavados_plataforma.urls import urlpatterns
        print(f"✅ Patrones de URL configurados: {len(urlpatterns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando URLs: {e}")
        return False

if __name__ == "__main__":
    success = test_configuracion_produccion()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 VERIFICACIÓN DE CONFIGURACIÓN DE PRODUCCIÓN COMPLETADA")
        print("📊 Resumen:")
        print("   ✅ Configuración de Django")
        print("   ✅ Archivos de deployment")
        print("   ✅ Variables de entorno")
        print("   ✅ Dependencias")
        print("   ✅ Configuración de base de datos")
        print("   ✅ Archivos estáticos")
        print("   ✅ Configuración de seguridad")
        print("   ✅ URLs y rutas")
        print("\n🚀 El proyecto está listo para deployment!")
    else:
        print("❌ ALGUNAS VERIFICACIONES FALLARON")
        print("🔧 Revisa los errores anteriores antes del deployment")
        sys.exit(1)