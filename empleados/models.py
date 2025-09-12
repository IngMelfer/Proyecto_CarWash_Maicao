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
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='empleado', verbose_name=_('Usuario'))
    numero_documento = models.CharField(max_length=20, unique=True, verbose_name=_('Número de Documento'))
    tipo_documento = models.ForeignKey('TipoDocumento', on_delete=models.PROTECT, related_name='empleados', verbose_name=_('Tipo de Documento'))
    nombre = models.CharField(max_length=100, verbose_name=_('Nombre'))
    apellido = models.CharField(max_length=100, verbose_name=_('Apellido'))
    telefono = models.CharField(max_length=15, verbose_name=_('Teléfono'))
    direccion = models.CharField(max_length=255, verbose_name=_('Dirección'))
    ciudad = models.CharField(max_length=100, verbose_name=_('Ciudad'))
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name=_('Fecha de Nacimiento'))
    cargo = models.ForeignKey('Cargo', on_delete=models.PROTECT, related_name='empleados', verbose_name=_('Cargo'))
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
    puntuacion = models.PositiveSmallIntegerField(verbose_name=_('Puntuación'), help_text=_('Calificación de 1 a 5 estrellas'))
    comentario = models.TextField(blank=True, verbose_name=_('Comentario'))
    fecha_calificacion = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Calificación'))
    
    class Meta:
        verbose_name = _('Calificación')
        verbose_name_plural = _('Calificaciones')
        ordering = ['-fecha_calificacion']
        # Un cliente solo puede calificar una vez a un empleado por servicio
        unique_together = ['empleado', 'servicio', 'cliente']
    
    def __str__(self):
        return f"{self.cliente} calificó a {self.empleado} con {self.puntuacion} estrellas"


class Incentivo(models.Model):
    """
    Modelo para gestionar los incentivos de los empleados basados en su desempeño.
    """
    empleado = models.ForeignKey('Empleado', on_delete=models.CASCADE, related_name='incentivos', verbose_name=_('Empleado'))
    nombre = models.CharField(max_length=100, verbose_name=_('Nombre del Incentivo'))
    descripcion = models.TextField(verbose_name=_('Descripción'))
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Monto'))
    fecha_otorgado = models.DateField(default=timezone.now, verbose_name=_('Fecha Otorgado'))
    periodo_inicio = models.DateField(verbose_name=_('Inicio del Período'))
    periodo_fin = models.DateField(verbose_name=_('Fin del Período'))
    promedio_calificacion = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, verbose_name=_('Promedio de Calificación'))
    servicios_completados = models.PositiveIntegerField(default=0, verbose_name=_('Servicios Completados'))
    
    class Meta:
        verbose_name = _('Incentivo')
        verbose_name_plural = _('Incentivos')
        ordering = ['-fecha_otorgado']
    
    def __str__(self):
        return f"{self.empleado} - {self.nombre} - {self.monto}"
