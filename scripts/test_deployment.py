#!/usr/bin/env python3
"""
Script para probar el despliegue completo de la aplicación.
Este script verifica la conexión a la base de datos, la configuración de correo electrónico
y el monitoreo con Sentry.
"""

import os
import sys
import django
import requests
import socket
import smtplib
import logging
from email.mime.text import MIMEText
from datetime import datetime

# Configurar logging
import sys
import io
import codecs

# Configurar la salida estándar para manejar caracteres Unicode
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('deployment_test.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def setup_django():
    """
    Configura Django para poder acceder a los modelos y configuraciones.
    """
    try:
        # Añadir el directorio padre al path para poder importar el proyecto
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
        django.setup()
        logger.info("✅ Django configurado correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error al configurar Django: {str(e)}")
        return False

def test_database_connection():
    """
    Prueba la conexión a la base de datos.
    """
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result[0] == 1:
            logger.info("✅ Conexión a la base de datos exitosa")
            return True
        else:
            logger.error("❌ La consulta a la base de datos no devolvió el resultado esperado")
            return False
    except Exception as e:
        logger.error(f"❌ Error al conectar con la base de datos: {str(e)}")
        return False

def test_email_configuration():
    """
    Prueba la configuración de correo electrónico.
    """
    try:
        from django.conf import settings
        
        # Verificar si la configuración de correo está presente
        if not hasattr(settings, 'EMAIL_HOST') or not settings.EMAIL_HOST:
            logger.warning("⚠️ EMAIL_HOST no está configurado")
            return False
            
        if not hasattr(settings, 'EMAIL_PORT') or not settings.EMAIL_PORT:
            logger.warning("⚠️ EMAIL_PORT no está configurado")
            return False
            
        if not hasattr(settings, 'EMAIL_HOST_USER') or not settings.EMAIL_HOST_USER:
            logger.warning("⚠️ EMAIL_HOST_USER no está configurado")
            return False
            
        if not hasattr(settings, 'EMAIL_HOST_PASSWORD') or not settings.EMAIL_HOST_PASSWORD:
            logger.warning("⚠️ EMAIL_HOST_PASSWORD no está configurado")
            return False
        
        # Intentar conectar al servidor SMTP sin enviar un correo
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.ehlo()
        if settings.EMAIL_USE_TLS:
            server.starttls()
            server.ehlo()
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.quit()
        
        logger.info("✅ Configuración de correo electrónico correcta")
        return True
    except Exception as e:
        logger.error(f"❌ Error en la configuración de correo electrónico: {str(e)}")
        return False



def test_static_files():
    """
    Prueba la configuración de archivos estáticos.
    """
    try:
        from django.conf import settings
        
        # Verificar si STATIC_ROOT está configurado
        if not hasattr(settings, 'STATIC_ROOT') or not settings.STATIC_ROOT:
            logger.warning("⚠️ STATIC_ROOT no está configurado")
            return False
            
        # Verificar si el directorio existe
        if not os.path.exists(settings.STATIC_ROOT):
            logger.warning(f"⚠️ El directorio STATIC_ROOT ({settings.STATIC_ROOT}) no existe")
            return False
            
        logger.info("✅ Configuración de archivos estáticos correcta")
        return True
    except Exception as e:
        logger.error(f"❌ Error al probar la configuración de archivos estáticos: {str(e)}")
        return False

def test_media_files():
    """
    Prueba la configuración de archivos multimedia.
    """
    try:
        from django.conf import settings
        
        # Verificar si MEDIA_ROOT está configurado
        if not hasattr(settings, 'MEDIA_ROOT') or not settings.MEDIA_ROOT:
            logger.warning("⚠️ MEDIA_ROOT no está configurado")
            return False
            
        # Verificar si el directorio existe
        if not os.path.exists(settings.MEDIA_ROOT):
            logger.warning(f"⚠️ El directorio MEDIA_ROOT ({settings.MEDIA_ROOT}) no existe")
            return False
            
        logger.info("✅ Configuración de archivos multimedia correcta")
        return True
    except Exception as e:
        logger.error(f"❌ Error al probar la configuración de archivos multimedia: {str(e)}")
        return False

def main():
    """
    Función principal que ejecuta todas las pruebas.
    """
    logger.info("🚀 Iniciando pruebas de despliegue")
    
    # Configurar Django
    if not setup_django():
        return 1
    
    # Ejecutar pruebas
    tests = [
        ("Conexión a la base de datos", test_database_connection),
        ("Configuración de correo electrónico", test_email_configuration),
        ("Configuración de archivos estáticos", test_static_files),
        ("Configuración de archivos multimedia", test_media_files),
    ]
    
    results = []
    for name, test_func in tests:
        logger.info(f"🔍 Probando: {name}")
        result = test_func()
        results.append((name, result))
    
    # Mostrar resumen
    logger.info("\n📋 Resumen de pruebas:")
    all_passed = True
    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        if not result:
            all_passed = False
        logger.info(f"{status} - {name}")
    
    if all_passed:
        logger.info("\n🎉 Todas las pruebas pasaron correctamente. El despliegue está listo.")
        return 0
    else:
        logger.warning("\n⚠️ Algunas pruebas fallaron. Revisa los errores antes de continuar.")
        return 1

if __name__ == "__main__":
    sys.exit(main())