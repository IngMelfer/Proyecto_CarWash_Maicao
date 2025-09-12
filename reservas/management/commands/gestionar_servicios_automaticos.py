"""Comando Django para gestionar automáticamente servicios.

Este comando realiza dos funciones principales:
1. Inicia automáticamente servicios confirmados 5 minutos después de la hora programada si el administrador no lo ha hecho.
2. Finaliza automáticamente servicios en proceso solo cuando se excede el tiempo de duración del servicio más un tiempo de tolerancia.

Uso:
    python manage.py gestionar_servicios_automaticos [--dry-run] [--minutos-inicio=5] [--minutos-fin=10]

Opciones:
    --dry-run: Ejecuta en modo simulación sin realizar cambios reales
    --minutos-inicio: Tiempo en minutos para iniciar automáticamente un servicio (default: 5)
    --minutos-fin: Tiempo adicional de tolerancia en minutos después de la duración del servicio (default: 10)
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from reservas.models import Reserva

class Command(BaseCommand):
    """Comando para gestionar automáticamente servicios.
    
    Este comando inicia automáticamente servicios confirmados 5 minutos después de su hora programada
    y finaliza automáticamente servicios en proceso solo cuando se excede el tiempo de duración del servicio
    más un tiempo adicional de tolerancia.
    """
    
    help = 'Gestiona automáticamente el inicio y finalización de servicios'

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
            '--minutos-inicio',
            type=int,
            default=5,
            help='Tiempo en minutos para iniciar automáticamente un servicio (por defecto: 5)',
        )
        parser.add_argument(
            '--minutos-fin',
            type=int,
            default=10,
            help='Tiempo adicional de tolerancia en minutos después de la duración del servicio (por defecto: 10)',
        )

    def handle(self, *args, **options):
        """Ejecuta el comando para gestionar servicios automáticos.
        
        Este método busca:
        1. Reservas confirmadas que llevan más de 5 minutos desde su hora programada y las inicia.
        2. Reservas en proceso que han excedido el tiempo de duración del servicio más un tiempo adicional de tolerancia y las finaliza.
        
        Args:
            *args: Argumentos posicionales
            **options: Opciones del comando, incluyendo 'dry-run', 'minutos-inicio' y 'minutos-fin'
        """
        dry_run = options.get('dry_run', False)
        minutos_inicio = options.get('minutos_inicio', 5)
        minutos_fin = options.get('minutos_fin', 10)
        now = timezone.now()
        
        # Gestionar inicio automático de servicios
        self._iniciar_servicios_automaticos(dry_run, minutos_inicio, now)
        
        # Gestionar finalización automática de servicios
        self._finalizar_servicios_automaticos(dry_run, minutos_fin, now)
    
    def _iniciar_servicios_automaticos(self, dry_run, minutos_inicio, now):
        """Inicia automáticamente servicios confirmados 5 minutos después de su hora programada.
        
        Args:
            dry_run: Si es True, solo simula las acciones sin realizarlas
            minutos_inicio: Minutos después de los cuales iniciar automáticamente un servicio
            now: Fecha y hora actual
        """
        # Calcular el tiempo límite para iniciar servicios (5 minutos después de la hora programada)
        
        # Buscar reservas confirmadas cuya hora programada ya pasó hace más de 5 minutos
        reservas_por_iniciar = Reserva.objects.filter(
            estado=Reserva.CONFIRMADA,
            fecha_hora__lt=now - timedelta(minutes=minutos_inicio)
        )
        
        # Contar cuántas reservas se encontraron
        count_inicio = reservas_por_iniciar.count()
        self.stdout.write(self.style.SUCCESS(f'Se encontraron {count_inicio} reservas confirmadas con más de {minutos_inicio} minutos desde su hora programada'))
        
        # Si no hay reservas para iniciar, terminar esta parte
        if count_inicio == 0:
            return
        
        # Procesar cada reserva por iniciar
        for reserva in reservas_por_iniciar:
            if dry_run:
                self.stdout.write(f'[SIMULACIÓN] Iniciando automáticamente la reserva {reserva.id} de {reserva.cliente} - {reserva.servicio}')
            else:
                # Iniciar el servicio
                reserva.iniciar_servicio()
                reserva.fecha_inicio_servicio = timezone.now()
                reserva.notas += f'\nServicio iniciado automáticamente {minutos_inicio} minutos después de la hora programada.'
                reserva.save(update_fields=['fecha_inicio_servicio', 'notas'])
                
                self.stdout.write(self.style.SUCCESS(f'Reserva {reserva.id} de {reserva.cliente} - {reserva.servicio} iniciada automáticamente'))
                
                # Crear notificación para el cliente
                from notificaciones.models import Notificacion
                Notificacion.objects.create(
                    cliente=reserva.cliente,
                    tipo=Notificacion.SERVICIO_INICIADO,
                    titulo='Servicio Iniciado',
                    mensaje=f'Su servicio {reserva.servicio.nombre} ha sido iniciado. Puede seguir el progreso en tiempo real.',
                )
    
    def _finalizar_servicios_automaticos(self, dry_run, minutos_fin, now):
        """Finaliza automáticamente servicios en proceso solo cuando se excede el tiempo del servicio.
        
        Args:
            dry_run: Si es True, solo simula las acciones sin realizarlas
            minutos_fin: Minutos adicionales de tolerancia después de la duración del servicio
            now: Fecha y hora actual
        """
        # Ya no usamos un tiempo fijo, sino que verificamos cada reserva individualmente
        
        # Buscar todas las reservas en proceso que tienen fecha de inicio
        reservas_en_proceso = Reserva.objects.filter(
            estado=Reserva.EN_PROCESO,
            fecha_inicio_servicio__isnull=False
        )
        
        # Contar cuántas reservas en proceso se encontraron
        count_proceso = reservas_en_proceso.count()
        self.stdout.write(self.style.SUCCESS(f'Se encontraron {count_proceso} reservas en proceso'))
        
        # Si no hay reservas en proceso, terminar esta parte
        if count_proceso == 0:
            return
        
        # Lista para almacenar las reservas que deben finalizarse
        reservas_por_finalizar = []
        
        # Verificar cada reserva en proceso para determinar si ha excedido su tiempo de servicio
        for reserva in reservas_en_proceso:
            # Calcular el tiempo esperado de finalización: hora de inicio + duración del servicio + tiempo de tolerancia
            duracion_servicio = reserva.servicio.duracion_minutos
            tiempo_esperado_fin = reserva.fecha_inicio_servicio + timedelta(minutes=duracion_servicio + minutos_fin)
            
            # Si ya pasó el tiempo esperado de finalización, agregar a la lista de reservas por finalizar
            if now > tiempo_esperado_fin:
                reservas_por_finalizar.append(reserva)
                self.stdout.write(f'Reserva {reserva.id} excedió su tiempo de servicio. Duración: {duracion_servicio} min, Inicio: {reserva.fecha_inicio_servicio}, Debió terminar: {tiempo_esperado_fin}')
        
        # Contar cuántas reservas deben finalizarse
        count_fin = len(reservas_por_finalizar)
        self.stdout.write(self.style.SUCCESS(f'Se encontraron {count_fin} reservas que excedieron su tiempo de servicio más {minutos_fin} minutos de tolerancia'))
        
        # Si no hay reservas para finalizar, terminar esta parte
        if count_fin == 0:
            return
        
        # Procesar cada reserva por finalizar
        for reserva in reservas_por_finalizar:
            if dry_run:
                self.stdout.write(f'[SIMULACIÓN] Finalizando automáticamente la reserva {reserva.id} de {reserva.cliente} - {reserva.servicio} que excedió su tiempo')
            else:
                # Finalizar el servicio
                if reserva.completar_servicio():
                    self.stdout.write(self.style.SUCCESS(f'Reserva {reserva.id} de {reserva.cliente} - {reserva.servicio} finalizada automáticamente por exceder tiempo'))
                    
                    # Crear notificación para el cliente
                    from notificaciones.models import Notificacion
                    Notificacion.objects.create(
                        cliente=reserva.cliente,
                        tipo=Notificacion.SERVICIO_FINALIZADO,
                        titulo='Servicio Finalizado',
                        mensaje=f'Su servicio {reserva.servicio.nombre} ha sido completado automáticamente al finalizar el tiempo estimado. ¡Gracias por confiar en nosotros!',
                    )
                else:
                    self.stdout.write(self.style.ERROR(f'No se pudo finalizar automáticamente la reserva {reserva.id}'))
        
        if not dry_run and count_fin > 0:
            self.stdout.write(self.style.SUCCESS(f'Proceso completado. Se finalizaron {count_fin} servicios automáticamente por exceder su tiempo.'))
        elif count_fin > 0:
            self.stdout.write(self.style.SUCCESS(f'Simulación completada. No se realizaron cambios.'))