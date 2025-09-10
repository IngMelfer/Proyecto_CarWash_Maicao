from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from reservas.models import Reserva

class Command(BaseCommand):
    help = 'Verifica y marca como incumplidas las reservas vencidas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar en modo simulación sin realizar cambios',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        now = datetime.now()
        
        # Buscar reservas pendientes o confirmadas cuya fecha y hora + duración del servicio ya haya pasado
        reservas_vencidas = Reserva.objects.filter(
            estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA],
            fecha_hora__lt=now
        )
        
        # Contar cuántas reservas vencidas se encontraron
        count = reservas_vencidas.count()
        self.stdout.write(self.style.SUCCESS(f'Se encontraron {count} reservas vencidas'))
        
        # Si no hay reservas vencidas, terminar
        if count == 0:
            return
        
        # Procesar cada reserva vencida
        for reserva in reservas_vencidas:
            # Calcular si el tiempo del servicio ya pasó
            tiempo_servicio = reserva.fecha_hora + timedelta(minutes=reserva.servicio.duracion_minutos)
            
            if tiempo_servicio < now:
                # La reserva está vencida y el tiempo del servicio ya pasó
                if dry_run:
                    self.stdout.write(f'[SIMULACIÓN] Marcando como INCUMPLIDA la reserva {reserva.id} de {reserva.cliente} - {reserva.servicio} programada para {reserva.fecha_hora}')
                else:
                    # Marcar como INCUMPLIDA usando el nuevo estado
                    reserva.estado = Reserva.INCUMPLIDA
                    reserva.notas += '\nReserva marcada como INCUMPLIDA automáticamente por sistema.'
                    reserva.save(update_fields=['estado', 'notas'])
                    
                    self.stdout.write(self.style.SUCCESS(f'Reserva {reserva.id} de {reserva.cliente} - {reserva.servicio} marcada como INCUMPLIDA'))
                    
                    # Crear notificación para el cliente
                    from notificaciones.models import Notificacion
                    Notificacion.objects.create(
                        cliente=reserva.cliente,
                        titulo='Reserva incumplida',
                        mensaje=f'Su reserva para {reserva.servicio.nombre} programada para {reserva.fecha_hora} ha sido marcada como incumplida por el sistema.',
                        tipo=Notificacion.RESERVA_CANCELADA
                    )
            else:
                self.stdout.write(f'La reserva {reserva.id} está pendiente pero aún no ha pasado el tiempo del servicio')
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f'Proceso completado. Se marcaron reservas incumplidas.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Simulación completada. No se realizaron cambios.'))