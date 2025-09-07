from django.core.management.base import BaseCommand
from reservas.models import DisponibilidadHoraria

class Command(BaseCommand):
    help = 'Crea registros de disponibilidad horaria para todos los días de la semana'

    def handle(self, *args, **options):
        # Eliminar registros existentes para evitar duplicados
        DisponibilidadHoraria.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Registros anteriores eliminados'))
        
        # Crear disponibilidad para cada día de la semana (0=Lunes, 6=Domingo)
        for dia in range(7):
            DisponibilidadHoraria.objects.create(
                dia_semana=dia,
                hora_inicio='06:00',
                hora_fin='18:00',
                capacidad_maxima=5,
                activo=True
            )
            self.stdout.write(self.style.SUCCESS(f'Creada disponibilidad para día {dia} de 06:00 a 18:00'))
        
        # Verificar que se hayan creado los registros
        registros = DisponibilidadHoraria.objects.all()
        self.stdout.write(self.style.SUCCESS(f'\nTotal de registros creados: {registros.count()}'))
        for reg in registros:
            self.stdout.write(f'Día: {reg.get_dia_semana_display()}, Hora inicio: {reg.hora_inicio}, Hora fin: {reg.hora_fin}')