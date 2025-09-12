from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from reservas.models import Servicio, DisponibilidadHoraria, Bahia, Reserva

class Command(BaseCommand):
    help = 'Verifica los horarios disponibles para un servicio específico'

    def handle(self, *args, **options):
        # Verificar que existan servicios
        servicios = Servicio.objects.filter(activo=True)
        if not servicios.exists():
            self.stdout.write(self.style.ERROR('No hay servicios activos en el sistema'))
            return
        
        # Usar el primer servicio para la prueba
        servicio = servicios.first()
        self.stdout.write(self.style.SUCCESS(f'Usando servicio: {servicio.nombre} (duración: {servicio.duracion_minutos} minutos)'))
        
        # Verificar disponibilidad horaria
        disponibilidad = DisponibilidadHoraria.objects.all()
        self.stdout.write(self.style.SUCCESS(f'Registros de disponibilidad horaria: {disponibilidad.count()}'))
        for disp in disponibilidad:
            self.stdout.write(f'Día: {disp.get_dia_semana_display()}, Horario: {disp.hora_inicio} - {disp.hora_fin}')
        
        # Verificar bahías activas
        bahias = Bahia.objects.filter(activo=True)
        self.stdout.write(self.style.SUCCESS(f'Bahías activas: {bahias.count()}'))
        for bahia in bahias:
            self.stdout.write(f'Bahía: {bahia.nombre}')
        
        # Fecha para la prueba (hoy)
        fecha = datetime.now().date()
        self.stdout.write(self.style.SUCCESS(f'Fecha de prueba: {fecha}'))
        
        # Obtener el día de la semana (0-6, donde 0 es lunes)
        dia_semana = fecha.weekday()
        self.stdout.write(f'Día de la semana: {dia_semana}')
        
        # Ya no se verifica si es una fecha especial
        
        # Buscar disponibilidad general para ese día
        disponibilidad_general = DisponibilidadHoraria.objects.filter(
            dia_semana=dia_semana,
            activo=True
        ).order_by('hora_inicio')
        
        self.stdout.write(self.style.SUCCESS(f'Disponibilidad para hoy: {disponibilidad_general.count()} registros'))
        
        # Crear horarios disponibles basados en la disponibilidad general y la duración del servicio
        horarios = []
        for disp in disponibilidad_general:
            # Crear intervalos exactos según la duración del servicio seleccionado
            # Empezamos desde la hora de inicio del día
            hora_actual = disp.hora_inicio
            
            # Generamos horarios en intervalos de 30 minutos para mostrar más opciones
            intervalo_minutos = 30
            
            self.stdout.write(f'Generando horarios para {disp.get_dia_semana_display()} {disp.hora_inicio} - {disp.hora_fin}')
            
            while hora_actual < disp.hora_fin:
                # Calculamos la hora de fin del servicio
                hora_fin = (datetime.combine(fecha, hora_actual) + timedelta(minutes=servicio.duracion_minutos)).time()
                
                # Solo agregamos el horario si el servicio cabe completamente en el horario disponible
                if hora_fin <= disp.hora_fin:
                    # Verificamos disponibilidad de bahías para este horario
                    hora_inicio_dt = timezone.make_aware(datetime.combine(fecha, hora_actual))
                    hora_fin_dt = timezone.make_aware(datetime.combine(fecha, hora_fin))
                    
                    # Obtenemos todas las bahías activas
                    bahias_activas = Bahia.objects.filter(activo=True)
                    
                    # Obtenemos las reservas que se solapan con este horario considerando la duración del servicio
                    reservas_solapadas = Reserva.objects.filter(
                        fecha_hora__lt=hora_fin_dt,
                        fecha_hora__gte=hora_inicio_dt,
                        estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
                    )
                    
                    # También considerar reservas que empezaron antes pero terminan durante nuestro horario
                    otras_reservas = Reserva.objects.filter(
                        fecha_hora__lt=hora_inicio_dt,
                        estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
                    )
                    
                    # Filtrar aquellas que se solapan con nuestro horario
                    for reserva in otras_reservas:
                        # Calcular la hora de fin de la reserva según la duración del servicio
                        fin_reserva = reserva.fecha_hora + timedelta(minutes=reserva.servicio.duracion_minutos)
                        # Si la reserva termina después de nuestra hora de inicio, hay solapamiento
                        if fin_reserva > hora_inicio_dt:
                            reservas_solapadas = reservas_solapadas | Reserva.objects.filter(id=reserva.id)
                    
                    # Obtener las bahías ocupadas
                    bahias_ocupadas = reservas_solapadas.values_list('bahia', flat=True).distinct()
                    
                    # Calcular bahías disponibles
                    bahias_disponibles = bahias_activas.exclude(id__in=bahias_ocupadas).count()
                    
                    # Solo agregamos el horario si hay bahías disponibles
                    if bahias_disponibles > 0:
                        horarios.append({
                            'hora_inicio': hora_actual.strftime('%H:%M'),
                            'hora_fin': hora_fin.strftime('%H:%M'),
                            'disponible': True,
                            'bahias_disponibles': bahias_disponibles
                        })
                
                # Avanzamos en intervalos de 30 minutos para mostrar más opciones
                hora_actual = (datetime.combine(fecha, hora_actual) + timedelta(minutes=intervalo_minutos)).time()
        
        # Mostrar los horarios generados
        self.stdout.write(self.style.SUCCESS(f'Total de horarios disponibles: {len(horarios)}'))
        for horario in horarios:
            self.stdout.write(f"Horario: {horario['hora_inicio']} a {horario['hora_fin']} - {horario['bahias_disponibles']} bahías disponibles")