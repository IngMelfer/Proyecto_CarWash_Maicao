from django.db import models
from django.utils.translation import gettext_lazy as _
from clientes.models import Cliente

# Create your models here.

class Notificacion(models.Model):
    """
    Modelo para almacenar las notificaciones enviadas a los clientes.
    """
    # Tipos de notificación
    RESERVA_CREADA = 'RC'
    RESERVA_CONFIRMADA = 'RF'
    RESERVA_CANCELADA = 'RA'
    SERVICIO_INICIADO = 'SI'
    SERVICIO_FINALIZADO = 'SF'
    CALIFICACION_RECIBIDA = 'CR'
    SERVICIO_ASIGNADO = 'SA'
    PROMOCION = 'PR'
    PUNTOS_ACUMULADOS = 'PA'
    PUNTOS_REDIMIDOS = 'PR'
    OTRO = 'OT'
    
    TIPO_CHOICES = [
        (RESERVA_CREADA, _('Reserva Creada')),
        (RESERVA_CONFIRMADA, _('Reserva Confirmada')),
        (RESERVA_CANCELADA, _('Reserva Cancelada')),
        (SERVICIO_INICIADO, _('Servicio Iniciado')),
        (SERVICIO_FINALIZADO, _('Servicio Finalizado')),
        (CALIFICACION_RECIBIDA, _('Calificación Recibida')),
        (SERVICIO_ASIGNADO, _('Servicio Asignado')),
        (PROMOCION, _('Promoción')),
        (PUNTOS_ACUMULADOS, _('Puntos Acumulados')),
        (PUNTOS_REDIMIDOS, _('Puntos Redimidos')),
        (OTRO, _('Otro')),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='notificaciones', verbose_name=_('Cliente'))
    reserva = models.ForeignKey('reservas.Reserva', on_delete=models.CASCADE, null=True, blank=True, related_name='notificaciones', verbose_name=_('Reserva'))
    tipo = models.CharField(max_length=2, choices=TIPO_CHOICES, verbose_name=_('Tipo'))
    titulo = models.CharField(max_length=100, verbose_name=_('Título'))
    mensaje = models.TextField(verbose_name=_('Mensaje'))
    leida = models.BooleanField(default=False, verbose_name=_('Leída'))
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Creación'))
    fecha_lectura = models.DateTimeField(null=True, blank=True, verbose_name=_('Fecha de Lectura'))
    
    class Meta:
        verbose_name = _('Notificación')
        verbose_name_plural = _('Notificaciones')
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.cliente} - {self.get_tipo_display()} - {self.fecha_creacion}"
    
    def marcar_como_leida(self):
        """
        Marca la notificación como leída y registra la fecha de lectura.
        """
        from django.utils import timezone
        
        if not self.leida:
            self.leida = True
            self.fecha_lectura = timezone.now()
            self.save(update_fields=['leida', 'fecha_lectura'])
            return True
        return False


class ConfiguracionNotificaciones(models.Model):
    """
    Modelo para almacenar las preferencias de notificaciones de los clientes.
    """
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='configuracion_notificaciones', verbose_name=_('Cliente'))
    email = models.BooleanField(default=True, verbose_name=_('Notificaciones por Email'))
    push = models.BooleanField(default=True, verbose_name=_('Notificaciones Push'))
    sms = models.BooleanField(default=False, verbose_name=_('Notificaciones SMS'))
    reservas = models.BooleanField(default=True, verbose_name=_('Notificaciones de Reservas'))
    servicios = models.BooleanField(default=True, verbose_name=_('Notificaciones de Servicios'))
    promociones = models.BooleanField(default=True, verbose_name=_('Notificaciones de Promociones'))
    puntos = models.BooleanField(default=True, verbose_name=_('Notificaciones de Puntos'))
    
    class Meta:
        verbose_name = _('Configuración de Notificaciones')
        verbose_name_plural = _('Configuraciones de Notificaciones')
    
    def __str__(self):
        return f"Configuración de {self.cliente}"
    
    def puede_recibir_notificacion(self, tipo_notificacion):
        """
        Verifica si el cliente puede recibir un tipo específico de notificación.
        """
        if not self.cliente.recibir_notificaciones:
            return False
            
        if tipo_notificacion in [Notificacion.RESERVA_CREADA, Notificacion.RESERVA_CONFIRMADA, Notificacion.RESERVA_CANCELADA]:
            return self.reservas
        elif tipo_notificacion in [Notificacion.SERVICIO_INICIADO, Notificacion.SERVICIO_FINALIZADO]:
            return self.servicios
        elif tipo_notificacion == Notificacion.PROMOCION:
            return self.promociones
        elif tipo_notificacion in [Notificacion.PUNTOS_ACUMULADOS, Notificacion.PUNTOS_REDIMIDOS]:
            return self.puntos
        return True
