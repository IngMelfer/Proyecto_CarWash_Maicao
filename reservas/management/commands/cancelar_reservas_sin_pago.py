"""
Comando Django para cancelar automáticamente reservas pendientes sin pago.

Este comando identifica reservas que han permanecido en estado pendiente por más
del tiempo configurado (por defecto 15 minutos) y las cancela automáticamente,
liberando los horarios reservados y notificando a los clientes.

Uso:
    python manage.py cancelar_reservas_sin_pago [--dry-run] [--minutos=15]

Opciones:
    --dry-run: Ejecuta en modo simulación sin realizar cambios reales
    --minutos: Tiempo en minutos para considerar una reserva como abandonada (default: 15)
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from reservas.models import Reserva

class Command(BaseCommand):
    """Comando para cancelar reservas pendientes sin pago.
    
    Este comando identifica y cancela automáticamente las reservas que han permanecido
    en estado pendiente por más del tiempo configurado (por defecto 15 minutos).
    Al cancelar las reservas, también libera los horarios y notifica a los clientes.
    """
    
    help = 'Cancela las reservas pendientes que llevan más de 15 minutos sin pago'

    def add_arguments(self, parser):
        """Configura los argumentos del comando.
        
        Args:
            parser: El parser de argumentos de Django
        """
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar en modo simulación sin realizar cambios',
        )
        parser.add_argument(
            '--minutos',
            type=int,
            default=15,
            help='Tiempo en minutos para cancelar reservas pendientes (por defecto: 15)',
        )

    def handle(self, *args, **options):
        """Ejecuta el comando para cancelar reservas sin pago.
        
        Este método busca reservas pendientes creadas antes del tiempo límite configurado,
        las cancela, libera los horarios asociados y notifica a los clientes.
        
        Args:
            *args: Argumentos posicionales
            **options: Opciones del comando, incluyendo 'dry-run' y 'minutos'
        """
        dry_run = options.get('dry_run', False)
        minutos = options.get('minutos', 15)
        now = timezone.now()
        
        # Calcular el tiempo límite (ahora menos los minutos configurados)
        tiempo_limite = now - timedelta(minutes=minutos)
        
        # Buscar reservas pendientes creadas antes del tiempo límite
        reservas_sin_pago = Reserva.objects.filter(
            estado=Reserva.PENDIENTE,
            fecha_creacion__lt=tiempo_limite
        )
        
        # Contar cuántas reservas sin pago se encontraron
        count = reservas_sin_pago.count()
        self.stdout.write(self.style.SUCCESS(f'Se encontraron {count} reservas pendientes con más de {minutos} minutos sin pago'))
        
        # Si no hay reservas sin pago, terminar
        if count == 0:
            return
        
        # Procesar cada reserva sin pago
        for reserva in reservas_sin_pago:
            if dry_run:
                self.stdout.write(f'[SIMULACIÓN] Cancelando la reserva {reserva.id} de {reserva.cliente} - {reserva.servicio} creada hace más de {minutos} minutos')
            else:
                # Cancelar la reserva
                reserva.estado = Reserva.CANCELADA
                reserva.notas += f'\nReserva cancelada automáticamente por falta de pago después de {minutos} minutos.'
                reserva.fecha_actualizacion = timezone.now()
                reserva.save(update_fields=['estado', 'notas', 'fecha_actualizacion'])
                
                self.stdout.write(self.style.SUCCESS(f'Reserva {reserva.id} de {reserva.cliente} - {reserva.servicio} cancelada por falta de pago'))
                
                # Decrementar contador de reservas en el horario si existe
                from reservas.models import HorarioDisponible
                horarios = HorarioDisponible.objects.filter(
                    fecha=reserva.fecha_hora.date(),
                    hora_inicio__lte=reserva.fecha_hora.time(),
                    hora_fin__gt=reserva.fecha_hora.time()
                )
                
                for horario in horarios:
                    horario.decrementar_reservas()
                
                # Crear notificación para el cliente
                from notificaciones.models import Notificacion
                Notificacion.objects.create(
                    cliente=reserva.cliente,
                    tipo=Notificacion.RESERVA_CANCELADA,
                    titulo='Reserva Cancelada',
                    mensaje=f'Su reserva para {reserva.servicio.nombre} programada para {reserva.fecha_hora.strftime("%d/%m/%Y a las %H:%M")} ha sido cancelada automáticamente por falta de pago.',
                )
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f'Proceso completado. Se cancelaron {count} reservas por falta de pago.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Simulación completada. No se realizaron cambios.'))