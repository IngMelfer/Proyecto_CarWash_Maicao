from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Create your models here.

class TipoDocumento(models.Model):
    """
    Modelo para almacenar los tipos de documento configurables por el Administrador del Sistema.
    """
    codigo = models.CharField(max_length=5, unique=True, verbose_name=_('Código'))
    nombre = models.CharField(max_length=100, verbose_name=_('Nombre'))
    activo = models.BooleanField(default=True, verbose_name=_('Activo'))
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Creación'))
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name=_('Última Actualización'))
    
    class Meta:
        verbose_name = _('Tipo de Documento')
        verbose_name_plural = _('Tipos de Documento')
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Cargo(models.Model):
    """
    Modelo para almacenar los cargos configurables por el Administrador del Sistema.
    """
    codigo = models.CharField(max_length=5, unique=True, verbose_name=_('Código'))
    nombre = models.CharField(max_length=100, verbose_name=_('Nombre'))
    descripcion = models.TextField(blank=True, verbose_name=_('Descripción'))
    activo = models.BooleanField(default=True, verbose_name=_('Activo'))
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Creación'))
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name=_('Última Actualización'))
    
    class Meta:
        verbose_name = _('Cargo')
        verbose_name_plural = _('Cargos')
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Empleado(models.Model):
    """
    Modelo para almacenar la información de los empleados del autolavado.
    Relacionado con el usuario de autenticación para el acceso al sistema.
    """
    # Opciones para el rol del empleado
    ROL_LAVADOR = 'lavador'
    ROL_ADMINISTRATIVO = 'administrativo'
    ROL_SUPERVISOR = 'supervisor'
    ROL_OTRO = 'otro'
    
    ROL_CHOICES = [
        (ROL_LAVADOR, _('Lavador')),
        (ROL_ADMINISTRATIVO, _('Administrativo')),
        (ROL_SUPERVISOR, _('Supervisor')),
        (ROL_OTRO, _('Otro')),
    ]
    
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='empleado', verbose_name=_('Usuario'))
    numero_documento = models.CharField(max_length=20, unique=True, verbose_name=_('Número de Documento'))
    tipo_documento = models.ForeignKey('TipoDocumento', on_delete=models.PROTECT, related_name='empleados', verbose_name=_('Tipo de Documento'))
    nombre = models.CharField(max_length=100, verbose_name=_('Nombre'))
    apellido = models.CharField(max_length=100, verbose_name=_('Apellido'))
    email_personal = models.EmailField(max_length=255, blank=True, null=True, verbose_name=_('Correo Personal'))
    telefono = models.CharField(max_length=15, verbose_name=_('Teléfono'))
    direccion = models.CharField(max_length=255, verbose_name=_('Dirección'))
    ciudad = models.CharField(max_length=100, verbose_name=_('Ciudad'))
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name=_('Fecha de Nacimiento'))
    cargo = models.ForeignKey('Cargo', on_delete=models.PROTECT, related_name='empleados', verbose_name=_('Cargo'))
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default=ROL_OTRO, verbose_name=_('Rol'))
    disponible = models.BooleanField(default=False, verbose_name=_('Disponible'))
    fecha_contratacion = models.DateField(verbose_name=_('Fecha de Contratación'))
    fotografia = models.ImageField(upload_to='empleados/fotografias/', null=True, blank=True, verbose_name=_('Fotografía'))
    activo = models.BooleanField(default=True, verbose_name=_('Activo'))
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Registro'))
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name=_('Última Actualización'))
    
    class Meta:
        verbose_name = _('Empleado')
        verbose_name_plural = _('Empleados')
        ordering = ['nombre', 'apellido']
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.cargo.nombre}"
        
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
        
    def es_lavador(self):
        return self.rol == self.ROL_LAVADOR
        
    def promedio_calificacion(self):
        """Retorna el promedio de calificaciones del empleado"""
        calificaciones = self.calificaciones.all()
        if not calificaciones:
            return 0
        return sum(c.puntuacion for c in calificaciones) / calificaciones.count()


class RegistroTiempo(models.Model):
    """
    Modelo para registrar el tiempo de trabajo de los empleados en cada servicio.
    """
    empleado = models.ForeignKey('Empleado', on_delete=models.CASCADE, related_name='registros_tiempo', verbose_name=_('Empleado'))
    servicio = models.ForeignKey('reservas.Servicio', on_delete=models.CASCADE, related_name='registros_tiempo', verbose_name=_('Servicio'))
    hora_inicio = models.DateTimeField(verbose_name=_('Hora de Inicio'))
    hora_fin = models.DateTimeField(null=True, blank=True, verbose_name=_('Hora de Finalización'))
    duracion_minutos = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Duración en Minutos'))
    notas = models.TextField(blank=True, verbose_name=_('Notas'))
    
    class Meta:
        verbose_name = _('Registro de Tiempo')
        verbose_name_plural = _('Registros de Tiempo')
        ordering = ['-hora_inicio']
    
    def __str__(self):
        return f"{self.empleado} - {self.servicio} - {self.hora_inicio.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Calcular la duración en minutos si hay hora de inicio y fin
        if self.hora_inicio and self.hora_fin:
            duracion = self.hora_fin - self.hora_inicio
            self.duracion_minutos = int(duracion.total_seconds() / 60)
        super().save(*args, **kwargs)


class Calificacion(models.Model):
    """
    Modelo para almacenar las calificaciones de los clientes a los empleados.
    """
    empleado = models.ForeignKey('Empleado', on_delete=models.CASCADE, related_name='calificaciones', verbose_name=_('Empleado'))
    servicio = models.ForeignKey('reservas.Servicio', on_delete=models.CASCADE, related_name='calificaciones_empleado', verbose_name=_('Servicio'))
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, related_name='calificaciones_dadas', verbose_name=_('Cliente'))
    reserva = models.ForeignKey('reservas.Reserva', on_delete=models.CASCADE, related_name='calificacion', verbose_name=_('Reserva'), null=True, blank=True)
    puntuacion = models.PositiveSmallIntegerField(verbose_name=_('Puntuación'), help_text=_('Calificación de 1 a 5 estrellas'))
    comentario = models.TextField(blank=True, verbose_name=_('Comentario'))
    fecha_calificacion = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Calificación'))
    
    class Meta:
        verbose_name = _('Calificación')
        verbose_name_plural = _('Calificaciones')
        ordering = ['-fecha_calificacion']
        # Un cliente solo puede calificar una vez por reserva específica
        unique_together = ['reserva', 'cliente']
    
    def __str__(self):
        return f"{self.cliente} calificó a {self.empleado} con {self.puntuacion} estrellas"


class ConfiguracionBonificacion(models.Model):
    """
    Modelo para configurar las reglas de bonificaciones que puede establecer el administrador.
    """
    TIPO_SERVICIOS = 'servicios'
    TIPO_MENSUAL = 'mensual'
    
    TIPO_CHOICES = [
        (TIPO_SERVICIOS, _('Por cantidad de servicios')),
        (TIPO_MENSUAL, _('Por desempeño mensual')),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name=_('Nombre de la Bonificación'))
    descripcion = models.TextField(verbose_name=_('Descripción'))
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name=_('Tipo de Bonificación'))
    
    # Criterios para bonificación
    servicios_requeridos = models.PositiveIntegerField(verbose_name=_('Servicios Requeridos'))
    calificacion_minima = models.DecimalField(max_digits=2, decimal_places=1, verbose_name=_('Calificación Mínima'))
    monto_bonificacion = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Monto de Bonificación'))
    
    # Configuración adicional
    activo = models.BooleanField(default=True, verbose_name=_('Activo'))
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Creación'))
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name=_('Última Actualización'))
    
    class Meta:
        verbose_name = _('Configuración de Bonificación')
        verbose_name_plural = _('Configuraciones de Bonificaciones')
        ordering = ['tipo', 'servicios_requeridos']
    
    def __str__(self):
        return f"{self.nombre} - {self.servicios_requeridos} servicios - {self.calificacion_minima}★ - ${self.monto_bonificacion}"


class Bonificacion(models.Model):
    """
    Modelo para configurar bonificaciones basadas en criterios específicos.
    """
    nombre = models.CharField(max_length=100, verbose_name=_('Nombre de la Bonificación'))
    descripcion = models.TextField(verbose_name=_('Descripción'))
    
    # Criterios de bonificación (opcionales - usar 0 o null para ignorar)
    dias_consecutivos_requeridos = models.PositiveIntegerField(
        default=0, 
        null=True,
        blank=True,
        verbose_name=_('Días Consecutivos Requeridos'),
        help_text=_('Número de días consecutivos que debe trabajar el empleado (dejar en 0 para ignorar este criterio)')
    )
    servicios_requeridos = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name=_('Servicios Requeridos'),
        help_text=_('Cantidad mínima de servicios que debe realizar (dejar en 0 para ignorar este criterio)')
    )
    calificacion_minima = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        null=True,
        blank=True,
        verbose_name=_('Calificación Mínima'),
        help_text=_('Calificación promedio mínima requerida (dejar en 0 para ignorar este criterio)')
    )
    
    # Bonificación
    monto_bonificacion = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_('Monto de Bonificación'),
        help_text=_('Monto en pesos que se otorgará al empleado')
    )
    
    # Control
    activo = models.BooleanField(default=True, verbose_name=_('Activo'))
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Creación'))
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name=_('Última Actualización'))
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='bonificaciones_creadas',
        verbose_name=_('Creado por')
    )

    class Meta:
        verbose_name = _('Bonificación')
        verbose_name_plural = _('Bonificaciones')
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} - ${self.monto_bonificacion}"

    def criterios_texto(self):
        """
        Devuelve una descripción legible de los criterios de la bonificación.
        Solo incluye criterios que están activos (> 0).
        """
        criterios = []
        
        if self.dias_consecutivos_requeridos and self.dias_consecutivos_requeridos > 0:
            criterios.append(f"{self.dias_consecutivos_requeridos} días consecutivos")
        
        if self.servicios_requeridos and self.servicios_requeridos > 0:
            criterios.append(f"{self.servicios_requeridos} servicios")
        
        if self.calificacion_minima and self.calificacion_minima > 0:
            criterios.append(f"calificación ≥ {self.calificacion_minima}")
        
        if not criterios:
            return "Sin criterios específicos"
        
        return " + ".join(criterios)


class BonificacionObtenida(models.Model):
    """
    Modelo para registrar las bonificaciones obtenidas por los empleados.
    """
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_REDIMIDA = 'redimida'
    ESTADO_CANCELADA = 'cancelada'

    ESTADOS_CHOICES = [
        (ESTADO_PENDIENTE, _('Pendiente de Redimir')),
        (ESTADO_REDIMIDA, _('Redimida')),
        (ESTADO_CANCELADA, _('Cancelada')),
    ]

    empleado = models.ForeignKey(
        'Empleado', 
        on_delete=models.CASCADE, 
        related_name='bonificaciones_obtenidas', 
        verbose_name=_('Empleado')
    )
    bonificacion = models.ForeignKey(
        'Bonificacion', 
        on_delete=models.CASCADE, 
        related_name='bonificaciones_otorgadas', 
        verbose_name=_('Bonificación')
    )
    
    # Datos del período evaluado
    fecha_inicio_periodo = models.DateField(verbose_name=_('Inicio del Período'))
    fecha_fin_periodo = models.DateField(verbose_name=_('Fin del Período'))
    
    # Métricas alcanzadas
    dias_consecutivos_trabajados = models.PositiveIntegerField(
        verbose_name=_('Días Consecutivos Trabajados')
    )
    servicios_realizados = models.PositiveIntegerField(
        verbose_name=_('Servicios Realizados')
    )
    calificacion_promedio = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        verbose_name=_('Calificación Promedio')
    )
    
    # Control de estado
    monto = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name=_('Monto')
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS_CHOICES, 
        default=ESTADO_PENDIENTE, 
        verbose_name=_('Estado')
    )
    fecha_obtencion = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_('Fecha de Obtención')
    )
    fecha_redencion = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name=_('Fecha de Redención')
    )
    redimida_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='bonificaciones_redimidas',
        verbose_name=_('Redimida por')
    )
    notas_redencion = models.TextField(
        blank=True, 
        verbose_name=_('Notas de Redención')
    )

    class Meta:
        verbose_name = _('Bonificación Obtenida')
        verbose_name_plural = _('Bonificaciones Obtenidas')
        ordering = ['-fecha_obtencion']
        unique_together = ['empleado', 'bonificacion', 'fecha_inicio_periodo', 'fecha_fin_periodo']

    def __str__(self):
        return f"{self.bonificacion.nombre} - {self.empleado.nombre_completo()} - ${self.monto}"

    def puede_ser_redimida(self):
        """Verifica si la bonificación puede ser redimida"""
        return self.estado == self.ESTADO_PENDIENTE

    def redimir(self, usuario_admin, notas=""):
        """Marca la bonificación como redimida"""
        if self.puede_ser_redimida():
            self.estado = self.ESTADO_REDIMIDA
            self.fecha_redencion = timezone.now()
            self.redimida_por = usuario_admin
            self.notas_redencion = notas
            self.save()
            return True
        return False

    def resumen_metricas(self):
        """Retorna un resumen de las métricas alcanzadas"""
        return {
            'dias_consecutivos': self.dias_consecutivos_trabajados,
            'servicios': self.servicios_realizados,
            'calificacion': float(self.calificacion_promedio),
            'cumple_criterios': self.cumple_todos_los_criterios()
        }

    def cumple_todos_los_criterios(self):
        """Verifica si cumple todos los criterios de la bonificación"""
        bonif = self.bonificacion
        return (
            self.dias_consecutivos_trabajados >= bonif.dias_consecutivos_requeridos and
            self.servicios_realizados >= bonif.servicios_requeridos and
            self.calificacion_promedio >= bonif.calificacion_minima
        )


class Incentivo(models.Model):
    """
    Modelo para almacenar los incentivos otorgados a los empleados.
    """
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_COBRADA = 'cobrada'
    ESTADO_CANCELADA = 'cancelada'

    ESTADOS_CHOICES = [
        (ESTADO_PENDIENTE, _('Pendiente')),
        (ESTADO_COBRADA, _('Cobrada')),
        (ESTADO_CANCELADA, _('Cancelada')),
    ]

    empleado = models.ForeignKey('Empleado', on_delete=models.CASCADE, related_name='incentivos', verbose_name=_('Empleado'))
    configuracion_bonificacion = models.ForeignKey('ConfiguracionBonificacion', on_delete=models.SET_NULL, null=True, blank=True, related_name='incentivos_otorgados', verbose_name=_('Configuración de Bonificación'))
    nombre = models.CharField(max_length=100, verbose_name=_('Nombre del Incentivo'))
    descripcion = models.TextField(verbose_name=_('Descripción'))
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Monto'))
    fecha_otorgado = models.DateField(default=timezone.now, verbose_name=_('Fecha Otorgado'))
    periodo_inicio = models.DateField(verbose_name=_('Inicio del Período'))
    periodo_fin = models.DateField(verbose_name=_('Fin del Período'))
    promedio_calificacion = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, verbose_name=_('Promedio de Calificación'))
    servicios_completados = models.PositiveIntegerField(default=0, verbose_name=_('Servicios Completados'))
    otorgado_automaticamente = models.BooleanField(default=False, verbose_name=_('Otorgado Automáticamente'))
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default=ESTADO_PENDIENTE, verbose_name=_('Estado'))
    fecha_cobro = models.DateTimeField(null=True, blank=True, verbose_name=_('Fecha de Cobro'))
    cobrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='bonificaciones_tramitadas', verbose_name=_('Cobrado por'))

    class Meta:
        verbose_name = _('Incentivo')
        verbose_name_plural = _('Incentivos')
        ordering = ['-fecha_otorgado']

    def __str__(self):
        return f"{self.nombre} - {self.empleado.nombre_completo()} - ${self.monto}"

    def marcar_como_cobrada(self, usuario):
        """Marca el incentivo como cobrado"""
        self.estado = self.ESTADO_COBRADA
        self.fecha_cobro = timezone.now()
        self.cobrado_por = usuario
        self.save()

    def puede_ser_cobrada(self):
        """Verifica si el incentivo puede ser cobrado"""
        return self.estado == self.ESTADO_PENDIENTE
