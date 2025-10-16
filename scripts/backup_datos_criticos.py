#!/usr/bin/env python
"""
Script para crear respaldo de datos críticos antes del reset de migraciones.
Ejecutar desde el directorio raíz del proyecto: python scripts/backup_datos_criticos.py
"""

import os
import sys
import django
from datetime import datetime
import json

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from django.core import serializers
from autenticacion.models import Usuario
from clientes.models import Cliente
from empleados.models import Empleado
from reservas.models import Reserva, Servicio, Bahia
from notificaciones.models import Notificacion

def crear_backup():
    """Crear respaldo de datos críticos"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_migraciones_{timestamp}"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    print(f"🔄 Creando respaldo en: {backup_dir}")
    
    # Modelos críticos a respaldar
    modelos_criticos = [
        (Usuario, 'usuarios'),
        (Cliente, 'clientes'), 
        (Empleado, 'empleados'),
        (Servicio, 'servicios'),
        (Bahia, 'bahias'),
        (Reserva, 'reservas'),
        (Notificacion, 'notificaciones'),
    ]
    
    resumen = {}
    
    for modelo, nombre in modelos_criticos:
        try:
            queryset = modelo.objects.all()
            count = queryset.count()
            
            if count > 0:
                # Serializar a JSON
                data = serializers.serialize('json', queryset, indent=2)
                
                # Guardar archivo
                filename = f"{backup_dir}/{nombre}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(data)
                
                print(f"✅ {nombre}: {count} registros respaldados")
                resumen[nombre] = count
            else:
                print(f"⚠️  {nombre}: Sin datos para respaldar")
                resumen[nombre] = 0
                
        except Exception as e:
            print(f"❌ Error respaldando {nombre}: {e}")
            resumen[nombre] = f"Error: {e}"
    
    # Guardar resumen
    with open(f"{backup_dir}/resumen_backup.json", 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'resumen': resumen,
            'total_modelos': len(modelos_criticos)
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 Respaldo completado en: {backup_dir}")
    print(f"📊 Total de modelos respaldados: {len([k for k, v in resumen.items() if isinstance(v, int) and v > 0])}")
    
    return backup_dir

if __name__ == "__main__":
    try:
        backup_dir = crear_backup()
        print(f"\n💡 Para restaurar en caso de emergencia:")
        print(f"   python manage.py loaddata {backup_dir}/*.json")
    except Exception as e:
        print(f"❌ Error general: {e}")
        sys.exit(1)