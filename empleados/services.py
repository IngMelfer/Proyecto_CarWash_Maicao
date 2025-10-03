from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Empleado, Incentivo, ConfiguracionBonificacion, Calificacion
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