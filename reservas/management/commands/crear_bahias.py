from django.core.management.base import BaseCommand
from reservas.models import Bahia

class Command(BaseCommand):
    help = 'Crea bahías iniciales para el sistema'

    def handle(self, *args, **options):
        # Verificar si ya existen bahías
        if Bahia.objects.exists():
            self.stdout.write(self.style.WARNING("Ya existen bahías en el sistema. No se crearán nuevas."))
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
            self.stdout.write(self.style.SUCCESS(f"Bahía creada: {bahia_data['nombre']}"))
        
        self.stdout.write(self.style.SUCCESS(f"Se crearon {len(bahias)} bahías exitosamente."))