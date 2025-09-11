from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Cliente(models.Model):
    """
    Modelo para almacenar la información de los clientes del autolavado.
    Relacionado con el usuario de autenticación para el acceso al sistema.
    """
    # Opciones para el tipo de documento
    CEDULA = 'CC'
    PASAPORTE = 'PA'
    EXTRANJERIA = 'CE'
    NIT = 'NI'
    
    TIPO_DOCUMENTO_CHOICES = [
        (CEDULA, _('Cédula de Ciudadanía')),
        (PASAPORTE, _('Pasaporte')),
        (EXTRANJERIA, _('Cédula de Extranjería')),
        (NIT, _('NIT')),
    ]
    
    numero_documento = models.CharField(max_length=20, unique=True, verbose_name=_('Número de Documento'))
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cliente', verbose_name=_('Usuario'))
    nombre = models.CharField(max_length=100, verbose_name=_('Nombre'))
    apellido = models.CharField(max_length=100, verbose_name=_('Apellido'))
    email = models.EmailField(verbose_name=_('Correo Electrónico'))
    tipo_documento = models.CharField(max_length=2, choices=TIPO_DOCUMENTO_CHOICES, default=CEDULA, verbose_name=_('Tipo de Documento'))
    telefono = models.CharField(max_length=15, verbose_name=_('Teléfono'))
    direccion = models.CharField(max_length=255, verbose_name=_('Dirección'))
    ciudad = models.CharField(max_length=100, verbose_name=_('Ciudad'))
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name=_('Fecha de Nacimiento'))
    saldo_puntos = models.PositiveIntegerField(default=0, verbose_name=_('Saldo de Puntos'))
    recibir_notificaciones = models.BooleanField(default=True, verbose_name=_('Recibir Notificaciones'))
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Registro'))
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name=_('Última Actualización'))
    
    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.numero_documento}"
    
    def get_puntos_disponibles(self):
        """
        Retorna el saldo de puntos disponibles para el cliente.
        """
        return self.saldo_puntos
    
    def acumular_puntos(self, puntos):
        """
        Acumula puntos al saldo del cliente.
        """
        self.saldo_puntos += puntos
        self.save(update_fields=['saldo_puntos'])
        return self.saldo_puntos
    
    def redimir_puntos(self, puntos):
        """
        Redime puntos del saldo del cliente si tiene suficientes.
        Retorna True si la redención fue exitosa, False en caso contrario.
        """
        if self.saldo_puntos >= puntos:
            self.saldo_puntos -= puntos
            self.save(update_fields=['saldo_puntos'])
            return True
        return False


class HistorialServicio(models.Model):
    """
    Modelo para almacenar el historial de servicios realizados a los clientes.
    """
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='historial_servicios', verbose_name=_('Cliente'))
    servicio = models.CharField(max_length=100, verbose_name=_('Servicio'))
    descripcion = models.TextField(blank=True, verbose_name=_('Descripción'))
    fecha_servicio = models.DateTimeField(verbose_name=_('Fecha del Servicio'))
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Monto'))
    puntos_ganados = models.PositiveIntegerField(default=0, verbose_name=_('Puntos Ganados'))
    comentarios = models.TextField(blank=True, verbose_name=_('Comentarios'))
    
    class Meta:
        verbose_name = _('Historial de Servicio')
        verbose_name_plural = _('Historial de Servicios')
        ordering = ['-fecha_servicio']
    
    def __str__(self):
        return f"{self.cliente} - {self.servicio} - {self.fecha_servicio}"
