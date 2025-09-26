#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================
WSGI CONFIGURATION FOR PYTHONANYWHERE
========================================

Archivo WSGI optimizado específicamente para PythonAnywhere.
Este archivo debe ser copiado al archivo WSGI de tu aplicación web en PythonAnywhere.

Ruta típica en PythonAnywhere: /var/www/tu_usuario_pythonanywhere_com_wsgi.py

Instrucciones de uso:
1. Copia este contenido al archivo WSGI de tu aplicación web
2. Reemplaza 'tu_usuario' con tu nombre de usuario de PythonAnywhere
3. Asegúrate de que la ruta del proyecto sea correcta
4. Verifica que el entorno virtual esté configurado correctamente
"""

import os
import sys
import logging
from pathlib import Path

# ========================================
# CONFIGURACIÓN DE LOGGING
# ========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ========================================
# CONFIGURACIÓN DE RUTAS
# ========================================
# IMPORTANTE: Reemplaza 'tu_usuario' con tu nombre de usuario de PythonAnywhere
PROJECT_PATH = '/home/tu_usuario/Proyecto_CarWash_Maicao'
VENV_PATH = '/home/tu_usuario/.virtualenvs/autolavados_env'

# Agregar el directorio del proyecto al Python path
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)
    logger.info(f"Agregado {PROJECT_PATH} al Python path")

# Agregar el directorio del entorno virtual si existe
venv_site_packages = os.path.join(VENV_PATH, 'lib', 'python3.10', 'site-packages')
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)
    logger.info(f"Agregado {venv_site_packages} al Python path")

# ========================================
# CARGA DE VARIABLES DE ENTORNO
# ========================================
try:
    from dotenv import load_dotenv
    
    # Cargar variables de entorno desde .env
    env_file = Path(PROJECT_PATH) / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        logger.info(f"Variables de entorno cargadas desde {env_file}")
    else:
        logger.warning(f"Archivo .env no encontrado en {env_file}")
        
    # Configurar variables de entorno específicas para PythonAnywhere
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
    os.environ.setdefault('PYTHONPATH', PROJECT_PATH)
    
    # Configuraciones específicas para producción
    os.environ.setdefault('DEBUG', 'False')
    os.environ.setdefault('USE_MYSQL', 'True')
    
    logger.info("Variables de entorno configuradas correctamente")
    
except ImportError:
    logger.error("python-dotenv no está instalado. Instalando desde requirements.txt")
    # Fallback: configurar variables manualmente
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')

# ========================================
# CONFIGURACIÓN DE DJANGO
# ========================================
try:
    from django.core.wsgi import get_wsgi_application
    from django.conf import settings
    
    # Configurar Django
    application = get_wsgi_application()
    
    logger.info("Aplicación Django configurada exitosamente")
    logger.info(f"DEBUG: {settings.DEBUG}")
    logger.info(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    logger.info(f"DATABASE ENGINE: {settings.DATABASES['default']['ENGINE']}")
    
except Exception as e:
    logger.error(f"Error al configurar Django: {str(e)}")
    raise

# ========================================
# VERIFICACIONES DE SALUD
# ========================================
def health_check():
    """Verificación básica de salud de la aplicación"""
    try:
        from django.core.management import execute_from_command_line
        from django.db import connection
        
        # Verificar conexión a la base de datos
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            
        logger.info("✅ Verificación de salud exitosa")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en verificación de salud: {str(e)}")
        return False

# Ejecutar verificación de salud al inicializar
if __name__ != '__main__':
    health_check()

# ========================================
# INFORMACIÓN DE DEBUG
# ========================================
logger.info("========================================")
logger.info("WSGI PYTHONANYWHERE - INFORMACIÓN DE DEBUG")
logger.info("========================================")
logger.info(f"Python version: {sys.version}")
logger.info(f"Python path: {sys.path[:3]}...")  # Solo los primeros 3 elementos
logger.info(f"Project path: {PROJECT_PATH}")
logger.info(f"Virtual env path: {VENV_PATH}")
logger.info(f"Django settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
logger.info("========================================")

# ========================================
# MANEJO DE ERRORES GLOBAL
# ========================================
def application_wrapper(environ, start_response):
    """Wrapper para manejar errores globales"""
    try:
        return application(environ, start_response)
    except Exception as e:
        logger.error(f"Error en aplicación WSGI: {str(e)}")
        # Retornar error 500
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [b'Internal Server Error - Check logs for details']

# Usar el wrapper en lugar de la aplicación directa
# application = application_wrapper  # Descomenta esta línea si quieres el wrapper

logger.info("🚀 WSGI configurado y listo para PythonAnywhere")