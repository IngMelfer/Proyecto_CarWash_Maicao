from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta, time
from reservas.models import DisponibilidadHoraria, HorarioDisponible, Bahia, Reserva

class Command(BaseCommand):
    help = 'Genera horarios disponibles a partir de la configuración de disponibilidad horaria'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=30,
            help='Número de días para los que generar horarios disponibles'
        )
        parser.add_argument(
            '--intervalo',
            type=int,
            default=30,
            help='Intervalo en minutos entre horarios disponibles'
        )
        parser.add_argument(
            '--forzar',
            action='store_true',
            help='Forzar la regeneración de horarios incluso si ya existen'
        )

    def handle(self, *args, **options):
        dias = options['dias']
        intervalo_minutos = options['intervalo']
        forzar = options['forzar']
        
        # Fecha actual
        fecha_actual = timezone.now().date()
        
        # Generar horarios para los próximos días
        for i in range(dias):
            fecha = fecha_actual + timedelta(days=i)
            
            # Verificar si ya existen horarios para esta fecha
            if not forzar and HorarioDisponible.objects.filter(fecha=fecha).exists():
                self.stdout.write(self.style.WARNING(f'Ya existen horarios para {fecha}. Omitiendo...'))
                continue
            
            # Obtener el día de la semana (0-6, donde 0 es lunes)
            dia_semana = fecha.weekday()
            
            # Buscar disponibilidad general para ese día
            disponibilidad_general = DisponibilidadHoraria.objects.filter(
                dia_semana=dia_semana,
                activo=True
            ).order_by('hora_inicio')
            
            if not disponibilidad_general.exists():
                self.stdout.write(self.style.WARNING(f'No hay disponibilidad configurada para el día {fecha} (día {dia_semana})'))
                continue
                
            self.stdout.write(self.style.SUCCESS(f'Generando horarios para {fecha} (día {dia_semana})'))
            
            # Si forzamos la regeneración, eliminar los horarios existentes para esta fecha
            if forzar:
                horarios_eliminados = HorarioDisponible.objects.filter(fecha=fecha).delete()
                self.stdout.write(self.style.WARNING(f'Eliminados {horarios_eliminados[0]} horarios existentes para {fecha}'))
            
            # Crear horarios disponibles basados en la disponibilidad general
            horarios_creados = 0
            for disp in disponibilidad_general:
                # Crear intervalos según el intervalo especificado
                hora_actual = disp.hora_inicio
                
                while hora_actual < disp.hora_fin:
                    # Calculamos la hora de fin del intervalo
                    hora_fin = (datetime.combine(fecha, hora_actual) + timedelta(minutes=intervalo_minutos)).time()
                    
                    # Solo agregamos el horario si cabe completamente en el horario disponible
                    if hora_fin <= disp.hora_fin:
                        # Crear el horario disponible
                        HorarioDisponible.objects.create(
                            fecha=fecha,
                            hora_inicio=hora_actual,
                            hora_fin=hora_fin,
                            disponible=True,
                            capacidad=disp.capacidad_maxima,
                            reservas_actuales=0
                        )
                        horarios_creados += 1
                    
                    # Avanzamos al siguiente intervalo
                    hora_actual = hora_fin
            
            self.stdout.write(self.style.SUCCESS(f'Creados {horarios_creados} horarios disponibles para {fecha}'))
        
        self.stdout.write(self.style.SUCCESS(f'Proceso completado. Se generaron horarios para {dias} días.'))