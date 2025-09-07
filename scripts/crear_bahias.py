from django.core.management.base import BaseCommand
from reservas.models import Bahia

def run():
    """Crear bahías iniciales"""
    # Verificar si ya existen bahías
    if Bahia.objects.exists():
        print("Ya existen bahías en el sistema. No se crearán nuevas.")
        return
    
    # Crear bahías iniciales
    bahias = [
        {"nombre": "Bahía 1", "descripcion": "Bahía principal", "activo": True},
        {"nombre": "Bahía 2", "descripcion": "Bahía secundaria", "activo": True},
        {"nombre": "Bahía 3", "descripcion": "Bahía para vehículos grandes", "activo": True},
        {"nombre": "Bahía 4", "descripcion": "Bahía para servicios rápidos", "activo": True},
        {"nombre": "Bahía 5", "descripcion": "Bahía para servicios especiales", "activo": True},
    ]
    
    for bahia_data in bahias:
        Bahia.objects.create(**bahia_data)
        print(f"Bahía creada: {bahia_data['nombre']}")
    
    print(f"Se crearon {len(bahias)} bahías exitosamente.")

if __name__ == "__main__":
    run()