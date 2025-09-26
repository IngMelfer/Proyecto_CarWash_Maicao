#!/usr/bin/env python
"""
Script de Diagnóstico para PythonAnywhere
Ayuda a identificar problemas comunes en el despliegue
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def verificar_variables_entorno():
    """Verifica que todas las variables de entorno necesarias estén configuradas"""
    print("=" * 60)
    print("VERIFICACIÓN DE VARIABLES DE ENTORNO")
    print("=" * 60)
    
    variables_requeridas = {
        'USE_MYSQL': 'Activar MySQL en lugar de SQLite',
        'DB_NAME': 'Nombre de la base de datos MySQL',
        'DB_USER': 'Usuario de la base de datos',
        'DB_PASSWORD': 'Contraseña de la base de datos',
        'DB_HOST': 'Host de la base de datos',
        'PYTHONANYWHERE_USERNAME': 'Username de PythonAnywhere',
        'SECRET_KEY': 'Clave secreta de Django',
        'DJANGO_SETTINGS_MODULE': 'Módulo de configuración de Django'
    }
    
    variables_opcionales = {
        'CUSTOM_DOMAIN': 'Dominio personalizado (opcional)',
        'SITE_URL': 'URL del sitio',
        'DEBUG': 'Modo debug (debe ser False en producción)',
        'EMAIL_HOST': 'Servidor de correo',
        'EMAIL_HOST_USER': 'Usuario de correo',
        'NEQUI_API_KEY': 'API Key de Nequi (si usas pagos)'
    }
    
    problemas = []
    
    print("\n📋 Variables Requeridas:")
    for var, descripcion in variables_requeridas.items():
        valor = os.getenv(var)
        if valor:
            # Ocultar valores sensibles
            if 'PASSWORD' in var or 'SECRET' in var or 'KEY' in var:
                valor_mostrar = '*' * len(valor) if len(valor) > 0 else 'NO CONFIGURADA'
            else:
                valor_mostrar = valor
            print(f"  ✅ {var}: {valor_mostrar}")
        else:
            print(f"  ❌ {var}: NO CONFIGURADA - {descripcion}")
            problemas.append(f"Variable {var} no configurada")
    
    print("\n📋 Variables Opcionales:")
    for var, descripcion in variables_opcionales.items():
        valor = os.getenv(var)
        if valor:
            if 'PASSWORD' in var or 'SECRET' in var or 'KEY' in var:
                valor_mostrar = '*' * len(valor) if len(valor) > 0 else 'NO CONFIGURADA'
            else:
                valor_mostrar = valor
            print(f"  ✅ {var}: {valor_mostrar}")
        else:
            print(f"  ⚠️  {var}: NO CONFIGURADA - {descripcion}")
    
    return problemas

def verificar_configuracion_django():
    """Verifica la configuración de Django"""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE CONFIGURACIÓN DE DJANGO")
    print("=" * 60)
    
    problemas = []
    
    try:
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings_production')
        django.setup()
        
        from django.conf import settings
        
        print("\n📋 Configuración de Base de Datos:")
        db_config = settings.DATABASES['default']
        print(f"  Engine: {db_config['ENGINE']}")
        print(f"  Name: {db_config['NAME']}")
        print(f"  User: {db_config['USER']}")
        print(f"  Host: {db_config['HOST']}")
        print(f"  Port: {db_config['PORT']}")
        
        print("\n📋 Configuración de CSRF:")
        if hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
            print(f"  CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
        else:
            print("  ❌ CSRF_TRUSTED_ORIGINS no configurado")
            problemas.append("CSRF_TRUSTED_ORIGINS no configurado")
        
        print("\n📋 Configuración de CORS:")
        if hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
            print(f"  CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")
        else:
            print("  ❌ CORS_ALLOWED_ORIGINS no configurado")
        
        print("\n📋 Configuración de Seguridad:")
        print(f"  DEBUG: {settings.DEBUG}")
        print(f"  ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        
        if settings.DEBUG:
            print("  ⚠️  DEBUG está activado en producción")
            problemas.append("DEBUG activado en producción")
        
    except Exception as e:
        print(f"  ❌ Error al cargar configuración de Django: {e}")
        problemas.append(f"Error en configuración de Django: {e}")
    
    return problemas

def verificar_conexion_bd():
    """Verifica la conexión a la base de datos"""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE CONEXIÓN A BASE DE DATOS")
    print("=" * 60)
    
    problemas = []
    
    try:
        from django.db import connection
        
        # Intentar conectar a la base de datos
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("  ✅ Conexión a base de datos exitosa")
            else:
                print("  ❌ Error en consulta de prueba")
                problemas.append("Error en consulta de prueba a la base de datos")
        
        # Verificar tablas principales
        print("\n📋 Verificando tablas principales:")
        tablas_importantes = [
            'auth_user',
            'reservas_servicio',
            'reservas_reserva',
            'clientes_cliente',
            'empleados_empleado'
        ]
        
        for tabla in tablas_importantes:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                    count = cursor.fetchone()[0]
                    print(f"  ✅ {tabla}: {count} registros")
            except Exception as e:
                print(f"  ❌ {tabla}: Error - {e}")
                problemas.append(f"Tabla {tabla} no accesible: {e}")
        
    except Exception as e:
        print(f"  ❌ Error de conexión a base de datos: {e}")
        problemas.append(f"Error de conexión a BD: {e}")
    
    return problemas

def verificar_migraciones():
    """Verifica el estado de las migraciones"""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE MIGRACIONES")
    print("=" * 60)
    
    problemas = []
    
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # Capturar la salida del comando showmigrations
        output = StringIO()
        call_command('showmigrations', '--plan', stdout=output)
        migraciones = output.getvalue()
        
        if '[X]' in migraciones:
            print("  ✅ Migraciones aplicadas encontradas")
        else:
            print("  ⚠️  No se encontraron migraciones aplicadas")
        
        # Verificar si hay migraciones pendientes
        output = StringIO()
        call_command('showmigrations', stdout=output)
        migraciones_estado = output.getvalue()
        
        if '[ ]' in migraciones_estado:
            print("  ❌ Hay migraciones pendientes")
            problemas.append("Migraciones pendientes encontradas")
            print("  💡 Ejecuta: python manage.py migrate")
        else:
            print("  ✅ Todas las migraciones están aplicadas")
        
    except Exception as e:
        print(f"  ❌ Error al verificar migraciones: {e}")
        problemas.append(f"Error al verificar migraciones: {e}")
    
    return problemas

def verificar_archivos_estaticos():
    """Verifica la configuración de archivos estáticos"""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE ARCHIVOS ESTÁTICOS")
    print("=" * 60)
    
    problemas = []
    
    try:
        from django.conf import settings
        
        print(f"  STATIC_URL: {settings.STATIC_URL}")
        print(f"  STATIC_ROOT: {settings.STATIC_ROOT}")
        
        # Verificar si el directorio de archivos estáticos existe
        if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
            if os.path.exists(settings.STATIC_ROOT):
                archivos = len([f for f in os.listdir(settings.STATIC_ROOT) if os.path.isfile(os.path.join(settings.STATIC_ROOT, f))])
                print(f"  ✅ Directorio STATIC_ROOT existe con {archivos} archivos")
            else:
                print("  ❌ Directorio STATIC_ROOT no existe")
                problemas.append("Directorio STATIC_ROOT no existe")
                print("  💡 Ejecuta: python manage.py collectstatic")
        
    except Exception as e:
        print(f"  ❌ Error al verificar archivos estáticos: {e}")
        problemas.append(f"Error en archivos estáticos: {e}")
    
    return problemas

def generar_reporte_final(todos_los_problemas):
    """Genera un reporte final con todos los problemas encontrados"""
    print("\n" + "=" * 60)
    print("REPORTE FINAL DE DIAGNÓSTICO")
    print("=" * 60)
    
    if not todos_los_problemas:
        print("  🎉 ¡No se encontraron problemas críticos!")
        print("  ✅ Tu aplicación debería funcionar correctamente en PythonAnywhere")
    else:
        print(f"  ⚠️  Se encontraron {len(todos_los_problemas)} problemas:")
        for i, problema in enumerate(todos_los_problemas, 1):
            print(f"    {i}. {problema}")
        
        print("\n💡 SOLUCIONES RECOMENDADAS:")
        print("  1. Configura las variables de entorno faltantes en PythonAnywhere")
        print("  2. Ejecuta las migraciones si hay pendientes: python manage.py migrate")
        print("  3. Recolecta archivos estáticos: python manage.py collectstatic")
        print("  4. Reinicia tu aplicación web en el dashboard de PythonAnywhere")
        print("  5. Revisa los logs de error en /var/log/tu_usuario.pythonanywhere.com.error.log")

def main():
    """Función principal del diagnóstico"""
    print("🔍 DIAGNÓSTICO DE DESPLIEGUE EN PYTHONANYWHERE")
    print("Este script te ayudará a identificar problemas comunes")
    print("=" * 60)
    
    todos_los_problemas = []
    
    # Ejecutar todas las verificaciones
    todos_los_problemas.extend(verificar_variables_entorno())
    todos_los_problemas.extend(verificar_configuracion_django())
    todos_los_problemas.extend(verificar_conexion_bd())
    todos_los_problemas.extend(verificar_migraciones())
    todos_los_problemas.extend(verificar_archivos_estaticos())
    
    # Generar reporte final
    generar_reporte_final(todos_los_problemas)
    
    print("\n📚 Para más ayuda, consulta:")
    print("  - GUIA_VARIABLES_ENTORNO_PYTHONANYWHERE.md")
    print("  - Logs de PythonAnywhere: /var/log/tu_usuario.pythonanywhere.com.error.log")
    print("  - Dashboard de PythonAnywhere: https://www.pythonanywhere.com/user/tu_usuario/")

if __name__ == "__main__":
    main()