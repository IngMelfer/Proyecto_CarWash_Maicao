from django.db.models import Count
import os
import sys
import django

# Configurar el entorno de Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from reservas.models import Vehiculo, Reserva
from django.db import transaction

def eliminar_vehiculos_duplicados():
    print("Buscando vehículos duplicados...")
    
    # Encontrar placas duplicadas por cliente
    duplicados = Vehiculo.objects.values('cliente', 'placa').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    total_duplicados = duplicados.count()
    print(f"Se encontraron {total_duplicados} placas duplicadas")
    
    if total_duplicados == 0:
        print("No hay vehículos duplicados para corregir.")
        return
    
    # Procesar cada grupo de duplicados
    for duplicado in duplicados:
        cliente_id = duplicado['cliente']
        placa = duplicado['placa']
        
        print(f"Procesando duplicados para cliente {cliente_id}, placa {placa}")
        
        # Obtener todos los vehículos duplicados ordenados por ID (el más antiguo primero)
        vehiculos = Vehiculo.objects.filter(
            cliente_id=cliente_id, 
            placa=placa
        ).order_by('id')
        
        # El primer vehículo se mantiene, los demás se eliminan
        vehiculo_principal = vehiculos.first()
        vehiculos_a_eliminar = vehiculos.exclude(id=vehiculo_principal.id)
        
        print(f"  - Manteniendo vehículo ID {vehiculo_principal.id}")
        print(f"  - Eliminando {vehiculos_a_eliminar.count()} vehículos duplicados")
        
        with transaction.atomic():
            # Actualizar todas las reservas que usan los vehículos duplicados
            for vehiculo in vehiculos_a_eliminar:
                reservas_afectadas = Reserva.objects.filter(vehiculo=vehiculo)
                print(f"  - Actualizando {reservas_afectadas.count()} reservas del vehículo ID {vehiculo.id}")
                
                # Actualizar las reservas para que usen el vehículo principal
                reservas_afectadas.update(vehiculo=vehiculo_principal)
                
                # Eliminar el vehículo duplicado
                vehiculo.delete()
    
    print("\nProceso completado. Se han eliminado todos los vehículos duplicados.")

if __name__ == "__main__":
    eliminar_vehiculos_duplicados()