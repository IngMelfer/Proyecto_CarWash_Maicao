from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from reservas.models import HorarioDisponible

class Command(BaseCommand):
    help = 'Borra todos los horarios disponibles de la base de datos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirmar la eliminación de todos los horarios disponibles'
        )

    def handle(self, *args, **options):
        if not options['confirmar']:
            self.stdout.write(
                self.style.WARNING(
                    'Esta acción eliminará TODOS los horarios disponibles de la base de datos.\n'
                    'Para confirmar, ejecute el comando con --confirmar'
                )
            )
            return

        # Obtener el número de horarios disponibles antes de borrarlos
        num_horarios = HorarioDisponible.objects.count()
        
        # Borrar todos los horarios disponibles
        HorarioDisponible.objects.all().delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Se han eliminado {num_horarios} horarios disponibles correctamente.'
            )
        )