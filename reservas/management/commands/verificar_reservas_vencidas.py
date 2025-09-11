from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from reservas.models import Reserva

"""
Comando Django para verificar y marcar como incumplidas las reservas vencidas.

Este comando identifica reservas que ya han pasado su fecha y hora programada
y no han sido completadas (están en estado PENDIENTE o CONFIRMADA). Estas reservas
son marcadas como INCUMPLIDA, lo que permite liberar recursos y mantener
estadísticas precisas sobre el cumplimiento de las citas.

Uso:
    python manage.py verificar_reservas_vencidas [--dry-run]

Opciones:
    --dry-run    Ejecuta en modo simulación sin realizar cambios reales
"""


class Command(BaseCommand):
    """
    Comando para verificar y marcar como incumplidas las reservas vencidas.
    
    Este comando busca reservas en estado PENDIENTE o CONFIRMADA cuya fecha y hora
    ya han pasado, y las marca como INCUMPLIDA. Esto permite mantener el sistema
    limpio y generar estadísticas precisas sobre el cumplimiento de las citas.
    
    Al marcar una reserva como incumplida, también se genera una notificación
    para el cliente y se actualiza la nota de la reserva con información sobre
    el incumplimiento.
    """
    
    help = 'Verifica y marca como incumplidas las reservas vencidas'

    def add_arguments(self, parser):
        """
        Define los argumentos aceptados por el comando.
        
        Args:
            parser: El parser de argumentos de Django
        """
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecuta en modo simulación sin realizar cambios',
        )

    def handle(self, *args, **options):
        """
        Ejecuta el comando para verificar y marcar reservas vencidas como incumplidas.
        
        Este método realiza las siguientes acciones:
        1. Identifica reservas PENDIENTES o CONFIRMADAS cuya fecha y hora ya pasó
        2. Para cada reserva vencida cuyo tiempo de servicio ya pasó:
           - Cambia su estado a INCUMPLIDA
           - Actualiza las notas con información sobre el cambio automático
           - Crea una notificación para el cliente
        
        Args:
            *args: Argumentos posicionales (no utilizados)
            **options: Opciones del comando, incluyendo 'dry_run'
        
        Returns:
            None
        """
        dry_run = options.get('dry_run', False)
        now = timezone.now()
        
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
                    reserva.fecha_actualizacion = timezone.now()
                    reserva.save(update_fields=['estado', 'notas', 'fecha_actualizacion'])
                    
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