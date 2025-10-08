from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class KPIConfiguracion(models.Model):
    class Entidad(models.TextChoices):
        CLIENTES = 'clientes', _('Clientes')
        SERVICIOS = 'servicios', _('Servicios')
        EMPLEADOS = 'empleados', _('Empleados')
        INGRESOS = 'ingresos', _('Ingresos')
        RESERVAS = 'reservas', _('Reservas')

    class Metrica(models.TextChoices):
        CUENTA = 'count', _('Conteo')
        SUMA = 'sum', _('Suma')
        PROMEDIO = 'avg', _('Promedio')
        MAXIMO = 'max', _('Máximo')
        MINIMO = 'min', _('Mínimo')

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='kpis_configurados')
    nombre = models.CharField(max_length=150)
    entidad = models.CharField(max_length=20, choices=Entidad.choices)
    metrica = models.CharField(max_length=20, choices=Metrica.choices)
    campo = models.CharField(max_length=100, help_text=_('Nombre del campo sobre el que se aplica la métrica (ej: Reserva.precio_final)'))
    estado_filtro = models.CharField(max_length=30, null=True, blank=True, help_text=_('Opcional: filtrar por estado (ej: completada, cancelada)'))
    periodo_dias = models.PositiveIntegerField(default=30, help_text=_('Rango en días para calcular la métrica'))
    umbral_alerta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text=_('Opcional: umbral para generar alertas'))
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Configuración KPI')
        verbose_name_plural = _('Configuraciones KPI')
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.nombre} ({self.entidad}/{self.metrica})"