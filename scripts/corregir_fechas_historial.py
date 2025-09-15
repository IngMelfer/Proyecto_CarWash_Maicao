#!/usr/bin/env python
"""
Script para corregir fechas en el historial de servicios.

Este script corrige los problemas de zona horaria en los registros existentes
del modelo HistorialServicio.
"""

import os
import sys
import django
from django.utils import timezone
import pytz

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

# Importar después de configurar Django
from clientes.models import HistorialServicio
from django.db import connection
from django.db.models import Q

def verificar_conexion_mysql():
    """
    Verifica que la conexión a MySQL tenga la zona horaria configurada correctamente.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT @@session.time_zone")
        db_timezone = cursor.fetchone()[0]
        print(f"Zona horaria actual de MySQL: {db_timezone}")
        
        # Configurar la zona horaria a America/Bogota si no lo está
        if db_timezone != '-05:00':
            print("Configurando zona horaria de MySQL a America/Bogota (COT)...")
            cursor.execute("SET time_zone = '-05:00'")
            cursor.execute("SELECT @@session.time_zone")
            db_timezone = cursor.fetchone()[0]
            print(f"Nueva zona horaria de MySQL: {db_timezone}")

def corregir_fechas_historial():
    """
    Corrige las fechas en el historial de servicios que puedan tener problemas de zona horaria.
    """
    print("Corrigiendo fechas en el historial de servicios...")
    
    # Verificar la conexión MySQL primero
    verificar_conexion_mysql()
    
    # Obtener todos los registros del historial
    registros = HistorialServicio.objects.all()
    print(f"Total de registros a revisar: {registros.count()}")
    
    # Contador de registros corregidos
    corregidos = 0
    
    # Zona horaria de Colombia
    colombia_tz = pytz.timezone('America/Bogota')
    
    for registro in registros:
        try:
            # Verificar si la fecha tiene información de zona horaria
            fecha_actual = registro.fecha_servicio
            
            # Si la fecha no tiene zona horaria, asignarle UTC
            if fecha_actual.tzinfo is None:
                print(f"Registro {registro.id}: Fecha sin zona horaria: {fecha_actual}")
                
                # Asumimos que la fecha está en hora local de Colombia
                # La convertimos a aware con zona horaria de Colombia
                fecha_aware = colombia_tz.localize(fecha_actual)
                
                # Luego la convertimos a UTC para guardarla
                fecha_utc = fecha_aware.astimezone(pytz.UTC)
                
                # Actualizar el registro
                registro.fecha_servicio = fecha_utc
                registro.save(update_fields=['fecha_servicio'])
                
                print(f"  → Corregido a: {registro.fecha_servicio}")
                corregidos += 1
            else:
                # La fecha ya tiene zona horaria, verificar que sea UTC
                if str(fecha_actual.tzinfo) != 'UTC':
                    print(f"Registro {registro.id}: Fecha con zona horaria no UTC: {fecha_actual}")
                    
                    # Convertir a UTC
                    fecha_utc = fecha_actual.astimezone(pytz.UTC)
                    
                    # Actualizar el registro
                    registro.fecha_servicio = fecha_utc
                    registro.save(update_fields=['fecha_servicio'])
                    
                    print(f"  → Corregido a: {registro.fecha_servicio}")
                    corregidos += 1
        except Exception as e:
            print(f"Error al procesar registro {registro.id}: {e}")
    
    print(f"\nTotal de registros corregidos: {corregidos}")

def main():
    """
    Función principal del script.
    """
    print("=== Iniciando corrección de fechas en historial de servicios ===")
    corregir_fechas_historial()
    print("=== Proceso completado ===")

if __name__ == "__main__":
    main()