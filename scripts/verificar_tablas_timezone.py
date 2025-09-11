#!/usr/bin/env python
import os
import sys
import django
import mysql.connector
from django.conf import settings

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

def verificar_tablas_timezone():
    """Verifica si las tablas de zona horaria están instaladas en MySQL"""
    print("=== Verificando tablas de zona horaria en MySQL ===")
    
    # Obtener configuración de la base de datos
    db_config = settings.DATABASES['default']
    
    if db_config['ENGINE'] != 'django.db.backends.mysql':
        print("No se está utilizando MySQL como base de datos.")
        return False
    
    try:
        # Conectar a MySQL
        conn = mysql.connector.connect(
            host=db_config['HOST'],
            user=db_config['USER'],
            password=db_config['PASSWORD'],
            database=db_config['NAME'],
            port=db_config['PORT']
        )
        
        cursor = conn.cursor()
        
        # Verificar si existen las tablas de zona horaria
        cursor.execute("SHOW TABLES LIKE 'time_zone%'")
        timezone_tables = cursor.fetchall()
        
        if not timezone_tables:
            print("ERROR: Las tablas de zona horaria no están instaladas en MySQL.")
            print("\nPara instalar las tablas de zona horaria, ejecute:")
            print("1. Descargue el archivo timezone_posix.sql desde MySQL")
            print("2. Ejecute: mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root -p mysql")
            print("   (En Windows, use la ruta adecuada a los archivos de zona horaria)")
            return False
        else:
            print("Las tablas de zona horaria están instaladas correctamente:")
            for table in timezone_tables:
                print(f"- {table[0]}")
            
            # Verificar si hay datos en las tablas
            cursor.execute("SELECT COUNT(*) FROM mysql.time_zone")
            count = cursor.fetchone()[0]
            if count == 0:
                print("\nADVERTENCIA: Las tablas de zona horaria existen pero no contienen datos.")
                return False
            else:
                print(f"\nLas tablas contienen datos ({count} registros en time_zone).")
                
                # Verificar la configuración actual de zona horaria
                cursor.execute("SELECT @@global.time_zone, @@session.time_zone")
                global_tz, session_tz = cursor.fetchone()
                print(f"\nConfiguración actual de zona horaria:")
                print(f"- Global: {global_tz}")
                print(f"- Sesión: {session_tz}")
                
                return True
    except Exception as e:
        print(f"Error al verificar las tablas de zona horaria: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def cargar_tablas_timezone():
    """Carga las tablas de zona horaria en MySQL"""
    print("\n=== Cargando tablas de zona horaria en MySQL ===")
    
    # Obtener configuración de la base de datos
    db_config = settings.DATABASES['default']
    
    try:
        # Conectar a MySQL
        conn = mysql.connector.connect(
            host=db_config['HOST'],
            user=db_config['USER'],
            password=db_config['PASSWORD'],
            database='mysql',  # Conectar a la base de datos mysql
            port=db_config['PORT']
        )
        
        cursor = conn.cursor()
        
        # Verificar si el usuario tiene privilegios para modificar la base de datos mysql
        cursor.execute("SHOW GRANTS FOR CURRENT_USER()")
        grants = cursor.fetchall()
        has_privileges = False
        
        for grant in grants:
            if 'ALL PRIVILEGES' in grant[0] or 'mysql.*' in grant[0]:
                has_privileges = True
                break
        
        if not has_privileges:
            print("ERROR: El usuario no tiene privilegios suficientes para cargar las tablas de zona horaria.")
            print("Necesita conectarse como usuario root o un usuario con privilegios en la base de datos mysql.")
            return False
        
        # En Windows, intentar cargar desde el archivo SQL si está disponible
        if os.name == 'nt':  # Windows
            sql_file = os.path.join(os.path.dirname(__file__), 'timezone_tables.sql')
            if os.path.exists(sql_file):
                print(f"Cargando tablas de zona horaria desde {sql_file}...")
                with open(sql_file, 'r') as f:
                    sql = f.read()
                    for statement in sql.split(';'):
                        if statement.strip():
                            cursor.execute(statement)
                conn.commit()
                print("Tablas de zona horaria cargadas correctamente.")
                return True
            else:
                print(f"No se encontró el archivo {sql_file}.")
                print("Por favor, descargue el archivo timezone_tables.sql y colóquelo en la carpeta scripts.")
                return False
        else:  # Unix/Linux
            # En sistemas Unix, intentar usar mysql_tzinfo_to_sql
            import subprocess
            try:
                print("Ejecutando mysql_tzinfo_to_sql para cargar las tablas de zona horaria...")
                # Ejecutar el comando mysql_tzinfo_to_sql
                cmd = f"mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u{db_config['USER']} -p{db_config['PASSWORD']} -h{db_config['HOST']} mysql"
                subprocess.run(cmd, shell=True, check=True)
                print("Tablas de zona horaria cargadas correctamente.")
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error al ejecutar mysql_tzinfo_to_sql: {e}")
                return False
    except Exception as e:
        print(f"Error al cargar las tablas de zona horaria: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    # Verificar si las tablas de zona horaria están instaladas
    if not verificar_tablas_timezone():
        # Si no están instaladas, intentar cargarlas
        print("\nIntentando cargar las tablas de zona horaria...")
        cargar_tablas_timezone()
        # Verificar nuevamente
        verificar_tablas_timezone()