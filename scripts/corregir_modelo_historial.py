#!/usr/bin/env python
import os
import sys
import django
from django.utils import timezone

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

# Importar después de configurar Django
from clientes.models import HistorialServicio
from django.db import connection

def corregir_modelo_historial():
    """Corrige el modelo HistorialServicio para manejar correctamente las zonas horarias"""
    print("=== Corrigiendo modelo HistorialServicio ===")
    
    try:
        # Verificar la configuración de zona horaria de MySQL
        with connection.cursor() as cursor:
            cursor.execute("SELECT @@session.time_zone")
            db_timezone = cursor.fetchone()[0]
            print(f"Zona horaria actual de MySQL: {db_timezone}")
            
            # Configurar la zona horaria a America/Bogota si no lo está
            if db_timezone != '-05:00':
                cursor.execute("SET time_zone = '-05:00'")
                print("Zona horaria de MySQL configurada a America/Bogota (COT)")
        
        # Obtener todos los registros de HistorialServicio
        registros = HistorialServicio.objects.all()
        print(f"Total de registros a procesar: {len(registros)}")
        
        # Crear una migración temporal para modificar la estructura de la tabla
        with connection.cursor() as cursor:
            # Modificar la columna fecha_servicio para usar DATETIME sin zona horaria
            cursor.execute("""
            ALTER TABLE clientes_historialservicio 
            MODIFY fecha_servicio DATETIME NOT NULL
            """)
            print("Columna fecha_servicio modificada a DATETIME sin zona horaria")
        
        # Actualizar cada registro para asegurar que las fechas estén en UTC
        registros_actualizados = 0
        for registro in registros:
            # Obtener la fecha actual
            fecha_actual = registro.fecha_servicio
            
            # Si la fecha tiene información de zona horaria, convertirla a UTC
            if fecha_actual.tzinfo is not None:
                fecha_utc = fecha_actual.astimezone(timezone.utc)
                registro.fecha_servicio = fecha_utc.replace(tzinfo=None)
                registro.save(update_fields=['fecha_servicio'])
                registros_actualizados += 1
        
        print(f"Registros actualizados: {registros_actualizados}")
        
        # Actualizar la configuración de Django para usar zona horaria UTC
        print("\nIMPORTANTE: Asegúrese de que en settings.py:")
        print("1. USE_TZ = False  # Cambiar a False para evitar problemas con MySQL")
        print("2. TIME_ZONE = 'America/Bogota'  # Usar Bogotá como zona horaria predeterminada")
        
        return True
    except Exception as e:
        print(f"Error al corregir el modelo HistorialServicio: {e}")
        return False

if __name__ == "__main__":
    corregir_modelo_historial()