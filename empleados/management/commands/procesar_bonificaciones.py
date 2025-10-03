from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from empleados.models import Empleado, ConfiguracionBonificacion
from empleados.services import BonificacionService
import logging

# Configurar logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Evalúa y otorga bonificaciones automáticamente a empleados que cumplan las condiciones'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecuta el comando sin realizar cambios en la base de datos',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Muestra información detallada del procesamiento',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Iniciando evaluación automática de bonificaciones...')
        )
        
        # Verificar configuraciones activas
        configuraciones_activas = ConfiguracionBonificacion.objects.filter(activo=True)
        if not configuraciones_activas.exists():
            self.stdout.write(
                self.style.WARNING('No hay configuraciones de bonificación activas.')
            )
            return
        
        if options['verbose']:
            self.stdout.write(f'Configuraciones activas encontradas: {configuraciones_activas.count()}')
            for config in configuraciones_activas:
                self.stdout.write(f'  - {config.nombre} ({config.get_tipo_display()})')
        
        # Procesar bonificaciones automáticas
        total_bonificaciones_otorgadas = 0
        empleados_procesados = 0
        errores = 0
        
        try:
            if options['dry_run']:
                # Modo dry-run: solo simular
                bonificaciones_creadas = BonificacionService.evaluar_bonificaciones_automaticas(dry_run=True)
                self.stdout.write(
                    f'[DRY-RUN] Se crearían {len(bonificaciones_creadas)} bonificaciones automáticas'
                )
                if options['verbose']:
                    for bonif in bonificaciones_creadas:
                        empleado = bonif['empleado']
                        config = bonif['configuracion']
                        self.stdout.write(
                            f'  - {empleado.nombre} {empleado.apellido}: {config.nombre} (${config.monto:,.0f})'
                        )
                total_bonificaciones_otorgadas = len(bonificaciones_creadas)
            else:
                # Modo real: procesar con transacción
                with transaction.atomic():
                    bonificaciones_creadas = BonificacionService.evaluar_bonificaciones_automaticas()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Se otorgaron {len(bonificaciones_creadas)} bonificaciones automáticas'
                        )
                    )
                    if options['verbose']:
                        for bonif in bonificaciones_creadas:
                            self.stdout.write(
                                f'  - {bonif.empleado.nombre} {bonif.empleado.apellido}: '
                                f'{bonif.nombre} (${bonif.monto:,.0f})'
                            )
                    total_bonificaciones_otorgadas = len(bonificaciones_creadas)
                
        except Exception as e:
            errores += 1
            logger.error(f'Error durante la evaluación automática: {str(e)}')
            self.stdout.write(
                self.style.ERROR(f'Error durante la evaluación automática: {str(e)}')
            )
        
        # Resumen final
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('RESUMEN DE LA EVALUACIÓN'))
        self.stdout.write('='*50)
        self.stdout.write(f'Bonificaciones otorgadas: {total_bonificaciones_otorgadas}')
        self.stdout.write(f'Errores: {errores}')
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('MODO DRY-RUN: No se realizaron cambios en la base de datos')
            )
        
        if errores > 0:
            self.stdout.write(
                self.style.ERROR(f'Se encontraron {errores} errores durante el procesamiento')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Evaluación completada exitosamente')
            )
        
        # Log del resultado
        logger.info(
            f'Evaluación automática de bonificaciones completada. '
            f'Bonificaciones otorgadas: {total_bonificaciones_otorgadas}, '
            f'Errores: {errores}'
        )