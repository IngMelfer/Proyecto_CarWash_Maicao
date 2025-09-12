from django.core.management.base import BaseCommand
from reservas.models import Reserva

class Command(BaseCommand):
    help = 'Verifica el estado de una reserva específica'

    def add_arguments(self, parser):
        parser.add_argument('reserva_id', type=int, help='ID de la reserva a verificar')

    def handle(self, *args, **options):
        reserva_id = options['reserva_id']
        
        try:
            reserva = Reserva.objects.get(id=reserva_id)
            self.stdout.write(f'Reserva ID: {reserva.id}')
            self.stdout.write(f'Cliente: {reserva.cliente.nombre} {reserva.cliente.apellido}')
            self.stdout.write(f'Vehículo: {reserva.vehiculo.marca} {reserva.vehiculo.modelo} ({reserva.vehiculo.placa})')
            self.stdout.write(f'Bahía: {reserva.bahia.nombre}')
            self.stdout.write(f'Servicio: {reserva.servicio.nombre}')
            self.stdout.write(f'Fecha y hora: {reserva.fecha_hora}')
            self.stdout.write(f'Estado: {reserva.get_estado_display()}')
            self.stdout.write(f'Fecha de inicio del servicio: {reserva.fecha_inicio_servicio or "No iniciado"}')
            self.stdout.write(f'Lavador: {reserva.lavador.get_full_name() if reserva.lavador else "No asignado"}')
            
            if reserva.estado == Reserva.EN_PROCESO:
                self.stdout.write(self.style.SUCCESS('El servicio se inició automáticamente'))
            else:
                self.stdout.write(self.style.ERROR('El servicio NO se inició automáticamente'))
                
        except Reserva.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'No existe una reserva con ID {reserva_id}'))