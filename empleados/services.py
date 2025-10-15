from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Empleado, Incentivo, ConfiguracionBonificacion, Calificacion, Bonificacion, BonificacionObtenida, RegistroTiempo
from reservas.models import Reserva


class BonificacionService:
    """
    Servicio para evaluar automáticamente las condiciones de bonificación
    y otorgar bonificaciones a empleados que cumplan los criterios.
    """
    
    @staticmethod
    def evaluar_bonificaciones_automaticas():
        """
        Evalúa todas las configuraciones de bonificación activas
        y otorga bonificaciones automáticas a empleados que cumplan las condiciones.
        """
        configuraciones = ConfiguracionBonificacion.objects.filter(activo=True)
        bonificaciones_otorgadas = []
        
        for config in configuraciones:
            empleados_elegibles = BonificacionService._obtener_empleados_elegibles(config)
            
            for empleado in empleados_elegibles:
                # Verificar si ya tiene una bonificación para esta configuración en el período actual
                if not BonificacionService._ya_tiene_bonificacion(empleado, config):
                    bonificacion = BonificacionService._crear_bonificacion_automatica(empleado, config)
                    bonificaciones_otorgadas.append(bonificacion)
        
        return bonificaciones_otorgadas
    
    @staticmethod
    def _obtener_empleados_elegibles(configuracion):
        """
        Obtiene los empleados que cumplen con las condiciones de la configuración.
        """
        empleados_elegibles = []
        empleados_activos = Empleado.objects.filter(activo=True)
        
        for empleado in empleados_activos:
            if BonificacionService._empleado_cumple_condiciones(empleado, configuracion):
                empleados_elegibles.append(empleado)
        
        return empleados_elegibles
    
    @staticmethod
    def _empleado_cumple_condiciones(empleado, configuracion):
        """
        Verifica si un empleado cumple con todas las condiciones de la configuración.
        """
        # Calcular el período de evaluación (último mes por defecto)
        fecha_fin = timezone.now().date()
        fecha_inicio = fecha_fin - timedelta(days=30)
        
        # Condición 1: Servicios completados
        servicios_completados = Reserva.objects.filter(
            lavador=empleado,
            estado='completada',
            fecha_reserva__range=[fecha_inicio, fecha_fin]
        ).count()
        
        if servicios_completados < configuracion.servicios_requeridos:
            return False
        
        # Condición 2: Calificación promedio mínima
        calificacion_promedio = Calificacion.objects.filter(
            empleado=empleado,
            fecha_calificacion__range=[fecha_inicio, fecha_fin]
        ).aggregate(promedio=Avg('puntuacion'))['promedio']
        
        if calificacion_promedio is None or calificacion_promedio < configuracion.calificacion_minima:
            return False
        
        return True
    
    @staticmethod
    def _ya_tiene_bonificacion(empleado, configuracion):
        """
        Verifica si el empleado ya tiene una bonificación para esta configuración
        en el período actual.
        """
        fecha_fin = timezone.now().date()
        fecha_inicio = fecha_fin - timedelta(days=30)
        
        return Incentivo.objects.filter(
            empleado=empleado,
            configuracion_bonificacion=configuracion,
            fecha_otorgado__range=[fecha_inicio, fecha_fin],
            otorgado_automaticamente=True
        ).exists()
    
    @staticmethod
    def _crear_bonificacion_automatica(empleado, configuracion):
        """
        Crea una bonificación automática para el empleado basada en la configuración.
        """
        fecha_fin = timezone.now().date()
        fecha_inicio = fecha_fin - timedelta(days=30)
        
        # Calcular estadísticas del empleado para el período
        servicios_completados = Reserva.objects.filter(
            lavador=empleado,
            estado='completada',
            fecha_reserva__range=[fecha_inicio, fecha_fin]
        ).count()
        
        calificacion_promedio = Calificacion.objects.filter(
            empleado=empleado,
            fecha_calificacion__range=[fecha_inicio, fecha_fin]
        ).aggregate(promedio=Avg('puntuacion'))['promedio'] or 0
        
        bonificacion = Incentivo.objects.create(
            empleado=empleado,
            configuracion_bonificacion=configuracion,
            nombre=f"Bonificación Automática - {configuracion.nombre}",
            descripcion=f"Bonificación otorgada automáticamente por cumplir los criterios: "
                       f"{servicios_completados} servicios completados, "
                       f"calificación promedio de {calificacion_promedio:.2f}",
            monto=configuracion.monto_bonificacion,
            fecha_otorgado=timezone.now().date(),
            periodo_inicio=fecha_inicio,
            periodo_fin=fecha_fin,
            promedio_calificacion=calificacion_promedio,
            servicios_completados=servicios_completados,
            otorgado_automaticamente=True,
            estado=Incentivo.ESTADO_PENDIENTE
        )
        
        return bonificacion
    
    @staticmethod
    def obtener_bonificaciones_pendientes(empleado=None):
        """
        Obtiene las bonificaciones pendientes de cobro.
        Si se especifica un empleado, filtra por ese empleado.
        """
        queryset = Incentivo.objects.filter(estado=Incentivo.ESTADO_PENDIENTE)
        
        if empleado:
            queryset = queryset.filter(empleado=empleado)
        
        return queryset.order_by('-fecha_otorgado')
    
    @staticmethod
    def cobrar_bonificacion(bonificacion_id, usuario_tramitador):
        """
        Marca una bonificación como cobrada.
        """
        try:
            bonificacion = Incentivo.objects.get(id=bonificacion_id)
            
            if bonificacion.puede_ser_cobrada():
                bonificacion.marcar_como_cobrada(usuario_tramitador)
                return True, "Bonificación cobrada exitosamente"
            else:
                return False, "La bonificación no puede ser cobrada"
                
        except Incentivo.DoesNotExist:
            return False, "Bonificación no encontrada"
    
    @staticmethod
    def obtener_progreso_bonificaciones(empleado):
        """
        Obtiene el progreso del empleado hacia las próximas bonificaciones.
        """
        configuraciones_activas = ConfiguracionBonificacion.objects.filter(activo=True)
        progreso = []
        
        # Calcular el período de evaluación (último mes)
        fecha_fin = timezone.now().date()
        fecha_inicio = fecha_fin - timedelta(days=30)
        
        for config in configuraciones_activas:
            # Verificar si ya tiene bonificación para esta configuración
            ya_tiene_bonificacion = BonificacionService._ya_tiene_bonificacion(empleado, config)
            
            if not ya_tiene_bonificacion:
                # Calcular progreso actual
                servicios_completados = Reserva.objects.filter(
                    lavador=empleado,
                    estado='completada',
                    fecha_reserva__range=[fecha_inicio, fecha_fin]
                ).count()
                
                calificacion_promedio = Calificacion.objects.filter(
                    empleado=empleado,
                    fecha_calificacion__range=[fecha_inicio, fecha_fin]
                ).aggregate(promedio=Avg('puntuacion'))['promedio'] or 0
                
                # Calcular porcentajes de progreso
                progreso_servicios = min(100, (servicios_completados / config.servicios_requeridos) * 100) if config.servicios_requeridos > 0 else 100
                progreso_calificacion = min(100, (calificacion_promedio / config.calificacion_minima) * 100) if config.calificacion_minima > 0 else 100
                
                progreso_item = {
                    'configuracion': config,
                    'servicios_completados': servicios_completados,
                    'servicios_requeridos': config.servicios_requeridos,
                    'calificacion_actual': calificacion_promedio,
                    'calificacion_minima': config.calificacion_minima,
                    'progreso_servicios': progreso_servicios,
                    'progreso_calificacion': progreso_calificacion,
                    'cumple_requisitos': servicios_completados >= config.servicios_requeridos and calificacion_promedio >= config.calificacion_minima,
                    'monto_bonificacion': config.monto_bonificacion
                }
                
                progreso.append(progreso_item)
        
        return progreso


class BonificacionServiceV2:
    """
    Servicio mejorado para gestionar el cálculo y otorgamiento automático de bonificaciones
    basado en los nuevos modelos Bonificacion y BonificacionObtenida.
    """
    
    @staticmethod
    def calcular_dias_consecutivos_trabajados(empleado, fecha_fin, dias_evaluar=30):
        """
        Calcula los días consecutivos trabajados por un empleado hasta una fecha específica.
        """
        fecha_inicio = fecha_fin - timedelta(days=dias_evaluar)
        
        # Obtener todos los días trabajados en el período
        registros = RegistroTiempo.objects.filter(
            empleado=empleado,
            fecha__range=[fecha_inicio, fecha_fin],
            hora_salida__isnull=False  # Solo días completos
        ).values_list('fecha', flat=True).distinct().order_by('-fecha')
        
        if not registros:
            return 0
        
        # Calcular días consecutivos desde la fecha más reciente
        dias_consecutivos = 0
        fecha_actual = fecha_fin
        
        for fecha_registro in registros:
            if fecha_registro == fecha_actual:
                dias_consecutivos += 1
                fecha_actual -= timedelta(days=1)
            else:
                break
        
        return dias_consecutivos
    
    @staticmethod
    def calcular_servicios_realizados(empleado, fecha_inicio, fecha_fin):
        """
        Calcula la cantidad de servicios realizados por un empleado en un período.
        """
        return Reserva.objects.filter(
            empleado_asignado=empleado,
            fecha_reserva__range=[fecha_inicio, fecha_fin],
            estado='completada'
        ).count()
    
    @staticmethod
    def calcular_calificacion_promedio(empleado, fecha_inicio, fecha_fin):
        """
        Calcula la calificación promedio de un empleado en un período.
        """
        # Obtener reservas completadas con calificación
        reservas_calificadas = Reserva.objects.filter(
            empleado_asignado=empleado,
            fecha_reserva__range=[fecha_inicio, fecha_fin],
            estado='completada',
            calificaciones__isnull=False
        )
        
        if not reservas_calificadas.exists():
            return 0.0
        
        # Calcular promedio de calificaciones
        promedio = Calificacion.objects.filter(
            reserva__in=reservas_calificadas
        ).aggregate(promedio=Avg('puntuacion'))['promedio']
        
        return float(promedio) if promedio else 0.0
    
    @staticmethod
    def evaluar_empleado_para_bonificacion(empleado, bonificacion, fecha_evaluacion=None):
        """
        Evalúa si un empleado cumple los criterios para una bonificación específica.
        Ahora soporta criterios flexibles - solo evalúa criterios que están definidos (> 0).
        """
        if fecha_evaluacion is None:
            fecha_evaluacion = timezone.now().date()
        
        # Definir período de evaluación (últimos 30 días por defecto)
        fecha_fin = fecha_evaluacion
        fecha_inicio = fecha_fin - timedelta(days=30)
        
        # Calcular métricas
        dias_consecutivos = BonificacionServiceV2.calcular_dias_consecutivos_trabajados(
            empleado, fecha_fin, dias_evaluar=bonificacion.dias_consecutivos_requeridos + 10 if bonificacion.dias_consecutivos_requeridos else 30
        )
        servicios_realizados = BonificacionServiceV2.calcular_servicios_realizados(
            empleado, fecha_inicio, fecha_fin
        )
        calificacion_promedio = BonificacionServiceV2.calcular_calificacion_promedio(
            empleado, fecha_inicio, fecha_fin
        )
        
        # Evaluar criterios de forma flexible - solo los que están definidos
        criterios_evaluados = []
        criterios_cumplidos = []
        
        # Evaluar días consecutivos solo si está definido
        if bonificacion.dias_consecutivos_requeridos and bonificacion.dias_consecutivos_requeridos > 0:
            cumple_dias = dias_consecutivos >= bonificacion.dias_consecutivos_requeridos
            criterios_evaluados.append('dias')
            if cumple_dias:
                criterios_cumplidos.append('dias')
        
        # Evaluar servicios solo si está definido
        if bonificacion.servicios_requeridos and bonificacion.servicios_requeridos > 0:
            cumple_servicios = servicios_realizados >= bonificacion.servicios_requeridos
            criterios_evaluados.append('servicios')
            if cumple_servicios:
                criterios_cumplidos.append('servicios')
        
        # Evaluar calificación solo si está definida
        if bonificacion.calificacion_minima and bonificacion.calificacion_minima > 0:
            cumple_calificacion = calificacion_promedio >= float(bonificacion.calificacion_minima)
            criterios_evaluados.append('calificacion')
            if cumple_calificacion:
                criterios_cumplidos.append('calificacion')
        
        # El empleado cumple si cumple TODOS los criterios que están definidos
        cumple_criterios = len(criterios_evaluados) > 0 and len(criterios_cumplidos) == len(criterios_evaluados)
        
        return {
            'cumple_criterios': cumple_criterios,
            'dias_consecutivos': dias_consecutivos,
            'servicios_realizados': servicios_realizados,
            'calificacion_promedio': calificacion_promedio,
            'fecha_inicio_periodo': fecha_inicio,
            'fecha_fin_periodo': fecha_fin,
            'criterios_detalle': {
                'criterios_evaluados': criterios_evaluados,
                'criterios_cumplidos': criterios_cumplidos,
                'cumple_dias': dias_consecutivos >= (bonificacion.dias_consecutivos_requeridos or 0),
                'cumple_servicios': servicios_realizados >= (bonificacion.servicios_requeridos or 0),
                'cumple_calificacion': calificacion_promedio >= float(bonificacion.calificacion_minima or 0)
            }
        }
    
    @staticmethod
    def otorgar_bonificacion(empleado, bonificacion, metricas):
        """
        Otorga una bonificación a un empleado si cumple los criterios.
        """
        # Verificar que no haya una bonificación duplicada para el mismo período
        bonificacion_existente = BonificacionObtenida.objects.filter(
            empleado=empleado,
            bonificacion=bonificacion,
            fecha_inicio_periodo=metricas['fecha_inicio_periodo'],
            fecha_fin_periodo=metricas['fecha_fin_periodo']
        ).exists()
        
        if bonificacion_existente:
            return None, "Ya existe una bonificación para este período"
        
        # Crear la bonificación obtenida
        bonificacion_obtenida = BonificacionObtenida.objects.create(
            empleado=empleado,
            bonificacion=bonificacion,
            fecha_inicio_periodo=metricas['fecha_inicio_periodo'],
            fecha_fin_periodo=metricas['fecha_fin_periodo'],
            dias_consecutivos_trabajados=metricas['dias_consecutivos'],
            servicios_realizados=metricas['servicios_realizados'],
            calificacion_promedio=metricas['calificacion_promedio'],
            monto=bonificacion.monto_bonificacion
        )
        
        return bonificacion_obtenida, "Bonificación otorgada exitosamente"
    
    @staticmethod
    def obtener_bonificaciones_pendientes_empleado(empleado):
        """
        Obtiene todas las bonificaciones pendientes de un empleado.
        """
        return BonificacionObtenida.objects.filter(
            empleado=empleado,
            estado=BonificacionObtenida.ESTADO_PENDIENTE
        ).select_related('bonificacion')
    
    @staticmethod
    def obtener_historial_bonificaciones_empleado(empleado):
        """
        Obtiene el historial completo de bonificaciones de un empleado.
        """
        return BonificacionObtenida.objects.filter(
            empleado=empleado
        ).select_related('bonificacion', 'redimida_por').order_by('-fecha_obtencion')
    
    @staticmethod
    def redimir_bonificacion(bonificacion_obtenida, usuario_admin, notas=""):
        """
        Redime una bonificación específica.
        """
        if bonificacion_obtenida.puede_ser_redimida():
            return bonificacion_obtenida.redimir(usuario_admin, notas)
        return False
    
    @staticmethod
    def obtener_estadisticas_bonificaciones():
        """
        Obtiene estadísticas generales del sistema de bonificaciones.
        """
        total_bonificaciones = BonificacionObtenida.objects.count()
        bonificaciones_pendientes = BonificacionObtenida.objects.filter(
            estado=BonificacionObtenida.ESTADO_PENDIENTE
        ).count()
        bonificaciones_redimidas = BonificacionObtenida.objects.filter(
            estado=BonificacionObtenida.ESTADO_REDIMIDA
        ).count()
        
        monto_total_pendiente = BonificacionObtenida.objects.filter(
            estado=BonificacionObtenida.ESTADO_PENDIENTE
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        monto_total_redimido = BonificacionObtenida.objects.filter(
            estado=BonificacionObtenida.ESTADO_REDIMIDA
        ).aggregate(total=Sum('monto'))['total'] or 0
        
        return {
            'total_bonificaciones': total_bonificaciones,
            'bonificaciones_pendientes': bonificaciones_pendientes,
            'bonificaciones_redimidas': bonificaciones_redimidas,
            'monto_total_pendiente': float(monto_total_pendiente),
            'monto_total_redimido': float(monto_total_redimido)
        }