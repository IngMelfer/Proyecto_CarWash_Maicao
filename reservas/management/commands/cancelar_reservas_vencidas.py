"""
Comando Django para cancelar automáticamente reservas vencidas.

Este comando identifica reservas que han pasado su fecha y hora programada
y siguen en estado PENDIENTE o CONFIRMADA, y las cancela automáticamente
por incumplimiento, liberando los horarios reservados y notificando a los clientes.

Uso:
    python manage.py cancelar_reservas_vencidas [--dry-run] [--horas=2]

Opciones:
    --dry-run: Ejecuta en modo simulación sin realizar cambios reales
    --horas: Tiempo en horas de gracia después de la fecha programada (default: 2)
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from reservas.models import Reserva
from notificaciones.models import Notificacion

class Command(BaseCommand):
    """Comando para cancelar reservas vencidas.
    
    Este comando identifica y cancela automáticamente las reservas que han pasado
    su fecha y hora programada y siguen en estado PENDIENTE o CONFIRMADA.
    Al cancelar las reservas, también libera los horarios y notifica a los clientes.
    """
    
    help = 'Cancela las reservas que han pasado su fecha programada y siguen pendientes o confirmadas'

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
            '--horas',
            type=int,
            default=2,
            help='Tiempo en horas de gracia después de la fecha programada (por defecto: 2)',
        )

    def handle(self, *args, **options):
        """Ejecuta el comando para cancelar reservas vencidas.
        
        Este método busca reservas pendientes o confirmadas cuya fecha programada
        ya pasó hace más del tiempo de gracia configurado, las cancela y notifica.
        
        Args:
            *args: Argumentos posicionales
            **options: Opciones del comando, incluyendo 'dry-run' y 'horas'
        """
        dry_run = options.get('dry_run', False)
        horas_gracia = options.get('horas', 2)
        now = timezone.now()
        
        # Calcular el tiempo límite (ahora menos las horas de gracia)
        tiempo_limite = now - timedelta(hours=horas_gracia)
        
        # Buscar reservas pendientes o confirmadas cuya fecha programada ya pasó
        reservas_vencidas = Reserva.objects.filter(
            estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA],
            fecha_hora__lt=tiempo_limite
        )
        
        # Contar cuántas reservas vencidas se encontraron
        count = reservas_vencidas.count()
        self.stdout.write(self.style.SUCCESS(f'Se encontraron {count} reservas vencidas con más de {horas_gracia} horas desde su fecha programada'))
        
        # Si no hay reservas vencidas, terminar
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No se encontraron reservas vencidas para cancelar.'))
            return
        
        # Procesar cada reserva vencida
        canceladas = 0
        for reserva in reservas_vencidas:
            if dry_run:
                self.stdout.write(f'[SIMULACIÓN] Cancelando la reserva {reserva.id} de {reserva.cliente} - {reserva.servicio} programada para {reserva.fecha_hora}')
            else:
                # Determinar el motivo de cancelación
                motivo = "No pago" if reserva.estado == Reserva.PENDIENTE else "Incumplimiento"
                
                # Cancelar la reserva
                reserva.estado = Reserva.CANCELADA
                reserva.notas += f'\nReserva cancelada automáticamente por {motivo.lower()} después de {horas_gracia} horas de la fecha programada.'
                reserva.fecha_actualizacion = timezone.now()
                reserva.save(update_fields=['estado', 'notas', 'fecha_actualizacion'])
                
                self.stdout.write(self.style.SUCCESS(f'Reserva {reserva.id} de {reserva.cliente} - {reserva.servicio} cancelada por {motivo.lower()}'))
                
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
                mensaje = f'Su reserva para {reserva.servicio.nombre} programada para {reserva.fecha_hora.strftime("%d/%m/%Y a las %H:%M")} ha sido cancelada automáticamente por {motivo.lower()}.'
                
                Notificacion.objects.create(
                    cliente=reserva.cliente,
                    tipo=Notificacion.RESERVA_CANCELADA,
                    titulo='Reserva Cancelada',
                    mensaje=mensaje,
                )
                
                canceladas += 1
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f'Proceso completado. Se cancelaron {canceladas} reservas vencidas.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Simulación completada. No se realizaron cambios.'))