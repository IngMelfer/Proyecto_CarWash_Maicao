from django.core.management.base import BaseCommand
from reservas.models import Bahia

class Command(BaseCommand):
    help = 'Crea bahías de prueba para el sistema'

    def handle(self, *args, **options):
        # Eliminar bahías existentes
        Bahia.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Bahías anteriores eliminadas'))
        
        # Crear 5 bahías activas
        for i in range(1, 6):
            Bahia.objects.create(
                nombre=f'Bahía {i}',
                descripcion=f'Bahía de prueba {i}',
                activo=True,
                tiene_camara=False
            )
            self.stdout.write(self.style.SUCCESS(f'Creada Bahía {i}'))
        
        # Verificar que se hayan creado las bahías
        bahias = Bahia.objects.filter(activo=True)
        self.stdout.write(self.style.SUCCESS(f'\nTotal de bahías activas creadas: {bahias.count()}'))
        for bahia in bahias:
            self.stdout.write(f'ID: {bahia.id}, Nombre: {bahia.nombre}, Activo: {bahia.activo}')