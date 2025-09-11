#!/usr/bin/env python
"""
Script para aplicar todas las soluciones de zona horaria en un solo paso.

Este script ejecuta todas las correcciones necesarias para resolver
los problemas de zona horaria en MySQL con Django.
"""

import os
import sys
import subprocess
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

# Importar después de configurar Django
from django.conf import settings

def ejecutar_script(script_path, descripcion):
    """
    Ejecuta un script Python y muestra su salida.
    """
    print(f"\n=== Ejecutando: {descripcion} ===")
    try:
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"Error al ejecutar {script_path}:")
            print(result.stderr)
            return False
        return True
    except Exception as e:
        print(f"Error al ejecutar {script_path}: {e}")
        return False

def ejecutar_sql(sql_path, descripcion):
    """
    Ejecuta un script SQL en MySQL.
    """
    print(f"\n=== Ejecutando SQL: {descripcion} ===")
    
    # Verificar que estamos usando MySQL
    if 'mysql' not in settings.DATABASES['default']['ENGINE']:
        print("Este script solo es necesario para MySQL. La base de datos actual no es MySQL.")
        return False
    
    # Obtener credenciales de la base de datos
    db_name = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    
    try:
        # Comando para ejecutar el script SQL
        cmd = f"mysql -u{db_user} -p{db_password} -h{db_host} -P{db_port} {db_name} < {sql_path}"
        print(f"Ejecutando comando: {cmd}")
        
        # En Windows, necesitamos usar shell=True
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error al ejecutar {sql_path}:")
            print(result.stderr)
            return False
            
        print("Script SQL ejecutado correctamente.")
        return True
    except Exception as e:
        print(f"Error al ejecutar {sql_path}: {e}")
        return False

def main():
    """
    Función principal que ejecuta todos los scripts de solución.
    """
    print("=== Iniciando aplicación de soluciones para problemas de zona horaria ===")
    
    # Ruta base del proyecto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Configurar MySQL para zonas horarias
    config_script = os.path.join(base_dir, 'scripts', 'configurar_mysql_timezone.py')
    if os.path.exists(config_script):
        ejecutar_script(config_script, "Configurar MySQL para zonas horarias")
    
    # 2. Ejecutar script SQL para configurar zona horaria
    sql_script = os.path.join(base_dir, 'scripts', 'fix_mysql_timezone.sql')
    if os.path.exists(sql_script):
        ejecutar_sql(sql_script, "Configurar zona horaria en MySQL")
    
    # 3. Corregir fechas existentes
    fix_script = os.path.join(base_dir, 'scripts', 'corregir_fechas_historial.py')
    if os.path.exists(fix_script):
        ejecutar_script(fix_script, "Corregir fechas en historial de servicios")
    
    print("\n=== Proceso completado ===")
    print("\nSi todo se ejecutó correctamente, el problema de zona horaria debería estar resuelto.")
    print("Reinicia el servidor Django para aplicar todos los cambios:")
    print("  python manage.py runserver")

if __name__ == "__main__":
    main()