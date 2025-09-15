#!/usr/bin/env python
"""
Script para configurar las zonas horarias en MySQL para Django.
Este script carga las tablas de zonas horarias en MySQL para que funcione correctamente con Django.
"""

import os
import sys
import subprocess
from django.conf import settings

# Añadir el directorio del proyecto al path para poder importar settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')

def configurar_mysql_timezone():
    """
    Configura las tablas de zonas horarias en MySQL para que funcione correctamente con Django.
    """
    print("Configurando zonas horarias en MySQL...")
    
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
    
    # Comando para cargar las zonas horarias
    # Primero verificamos si las tablas de zona horaria ya existen
    check_cmd = f"mysql -u{db_user} -p{db_password} -h{db_host} -P{db_port} -e \""
    check_cmd += "SELECT COUNT(*) FROM mysql.time_zone_name;\""
    
    try:
        # Intentar ejecutar el comando para verificar si las tablas ya existen
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
        
        # Si el comando falla, probablemente las tablas no existen
        if result.returncode != 0:
            print("Las tablas de zona horaria no existen. Procediendo a cargarlas...")
            
            # Comando para cargar las zonas horarias desde los archivos SQL de MySQL
            # Este comando asume que mysql_tzinfo_to_sql está disponible en el sistema
            timezone_cmd = "mysql_tzinfo_to_sql /usr/share/zoneinfo | "
            timezone_cmd += f"mysql -u{db_user} -p{db_password} -h{db_host} -P{db_port} mysql"
            
            print("Ejecutando comando para cargar zonas horarias:")
            print(timezone_cmd)
            
            # Ejecutar el comando
            load_result = subprocess.run(timezone_cmd, shell=True)
            
            if load_result.returncode == 0:
                print("¡Zonas horarias cargadas correctamente!")
                return True
            else:
                print("Error al cargar las zonas horarias.")
                print("Es posible que necesites ejecutar el siguiente comando manualmente:")
                print(timezone_cmd)
                return False
        else:
            print("Las tablas de zona horaria ya existen en MySQL.")
            return True
            
    except Exception as e:
        print(f"Error al verificar o cargar las zonas horarias: {e}")
        return False

def configurar_mysql_timezone_windows():
    """
    Configura las zonas horarias en MySQL para Windows.
    En Windows, el proceso es diferente ya que no tiene /usr/share/zoneinfo.
    """
    print("Configurando zonas horarias en MySQL para Windows...")
    
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
    
    # En Windows, necesitamos ejecutar comandos SQL directamente
    # para configurar la zona horaria del servidor MySQL
    commands = [
        "SET GLOBAL time_zone = '-05:00';",  # America/Bogota (COT)
        "SET time_zone = '-05:00';",        # America/Bogota para la sesión actual
        "FLUSH PRIVILEGES;"                 # Aplicar cambios
    ]
    
    try:
        for cmd in commands:
            mysql_cmd = f"mysql -u{db_user} -p{db_password} -h{db_host} -P{db_port} -e \"{cmd}\""
            print(f"Ejecutando: {mysql_cmd}")
            result = subprocess.run(mysql_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error al ejecutar comando: {cmd}")
                print(f"Error: {result.stderr}")
                return False
        
        print("Configuración de zona horaria completada.")
        print("IMPORTANTE: Para una solución permanente, edita el archivo my.ini o my.cnf")
        print("y añade la siguiente línea en la sección [mysqld]:")
        print("default-time-zone = '+00:00'")
        return True
            
    except Exception as e:
        print(f"Error al configurar la zona horaria: {e}")
        return False

def main():
    """
    Función principal que determina el sistema operativo y ejecuta la configuración adecuada.
    """
    if os.name == 'nt':  # Windows
        configurar_mysql_timezone_windows()
    else:  # Unix/Linux/Mac
        configurar_mysql_timezone()

if __name__ == "__main__":
    main()