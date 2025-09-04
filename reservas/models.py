from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from clientes.models import Cliente
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Servicio(models.Model):
    """
    Modelo para almacenar los tipos de servicios ofrecidos por el autolavado.
    """
    nombre = models.CharField(max_length=100, verbose_name=_('Nombre'))
    descripcion = models.TextField(verbose_name=_('Descripción'))
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Precio'))
    duracion_minutos = models.PositiveIntegerField(default=30, verbose_name=_('Duración (minutos)'))
    puntos_otorgados = models.PositiveIntegerField(default=0, verbose_name=_('Puntos Otorgados'))
    activo = models.BooleanField(default=True, verbose_name=_('Activo'))
    
    class Meta:
        verbose_name = _('Servicio')
        verbose_name_plural = _('Servicios')
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio}"


class Reserva(models.Model):
    """
    Modelo para gestionar las reservas de servicios por parte de los clientes.
    """
    # Estados de la reserva
    PENDIENTE = 'PE'
    CONFIRMADA = 'CO'
    EN_PROCESO = 'PR'
    COMPLETADA = 'CM'
    CANCELADA = 'CA'
    
    ESTADO_CHOICES = [
        (PENDIENTE, _('Pendiente')),
        (CONFIRMADA, _('Confirmada')),
        (EN_PROCESO, _('En Proceso')),
        (COMPLETADA, _('Completada')),
        (CANCELADA, _('Cancelada')),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='reservas', verbose_name=_('Cliente'))
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='reservas', verbose_name=_('Servicio'))
    fecha_hora = models.DateTimeField(verbose_name=_('Fecha y Hora'))
    estado = models.CharField(max_length=2, choices=ESTADO_CHOICES, default=PENDIENTE, verbose_name=_('Estado'))
    notas = models.TextField(blank=True, verbose_name=_('Notas'))
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Creación'))
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name=_('Última Actualización'))
    
    class Meta:
        verbose_name = _('Reserva')
        verbose_name_plural = _('Reservas')
        ordering = ['-fecha_hora']
        # Evitar reservas duplicadas para el mismo servicio y hora
        constraints = [
            models.UniqueConstraint(fields=['fecha_hora', 'servicio'], name='unique_reserva')
        ]
    
    def __str__(self):
        return f"{self.cliente} - {self.servicio} - {self.fecha_hora}"
    
    def cancelar(self):
        """
        Cancela la reserva si no está en proceso o completada.
        """
        if self.estado not in [self.EN_PROCESO, self.COMPLETADA]:
            self.estado = self.CANCELADA
            self.save(update_fields=['estado'])
            return True
        return False
    
    def confirmar(self):
        """
        Confirma la reserva si está pendiente.
        """
        if self.estado == self.PENDIENTE:
            self.estado = self.CONFIRMADA
            self.save(update_fields=['estado'])
            return True
        return False
    
    def iniciar_servicio(self):
        """
        Inicia el servicio si la reserva está confirmada.
        """
        if self.estado == self.CONFIRMADA:
            self.estado = self.EN_PROCESO
            self.save(update_fields=['estado'])
            return True
        return False
    
    def completar_servicio(self):
        """
        Completa el servicio si está en proceso.
        Acumula los puntos al cliente.
        """
        if self.estado == self.EN_PROCESO:
            self.estado = self.COMPLETADA
            self.save(update_fields=['estado'])
            
            # Acumular puntos al cliente
            self.cliente.acumular_puntos(self.servicio.puntos_otorgados)
            
            return True
        return False


class DisponibilidadHoraria(models.Model):
    """
    Modelo para gestionar la disponibilidad horaria del autolavado.
    """
    # Días de la semana
    LUNES = 0
    MARTES = 1
    MIERCOLES = 2
    JUEVES = 3
    VIERNES = 4
    SABADO = 5
    DOMINGO = 6
    
    DIA_CHOICES = [
        (LUNES, _('Lunes')),
        (MARTES, _('Martes')),
        (MIERCOLES, _('Miércoles')),
        (JUEVES, _('Jueves')),
        (VIERNES, _('Viernes')),
        (SABADO, _('Sábado')),
        (DOMINGO, _('Domingo')),
    ]
    
    dia_semana = models.PositiveSmallIntegerField(choices=DIA_CHOICES, verbose_name=_('Día de la Semana'))
    hora_inicio = models.TimeField(verbose_name=_('Hora de Inicio'))
    hora_fin = models.TimeField(verbose_name=_('Hora de Fin'))
    capacidad_maxima = models.PositiveSmallIntegerField(default=1, verbose_name=_('Capacidad Máxima'))
    activo = models.BooleanField(default=True, verbose_name=_('Activo'))
    
    class Meta:
        verbose_name = _('Disponibilidad Horaria')
        verbose_name_plural = _('Disponibilidades Horarias')
        ordering = ['dia_semana', 'hora_inicio']
    
    def __str__(self):
        return f"{self.get_dia_semana_display()} - {self.hora_inicio} a {self.hora_fin}"
    
    @classmethod
    def verificar_disponibilidad(cls, fecha_hora, servicio):
        """
        Verifica si hay disponibilidad para una fecha y hora específica.
        """
        # Obtener el día de la semana (0-6, donde 0 es lunes)
        dia_semana = fecha_hora.weekday()
        hora = fecha_hora.time()
        
        # Buscar disponibilidad para ese día y hora
        disponibilidad = cls.objects.filter(
            dia_semana=dia_semana,
            hora_inicio__lte=hora,
            hora_fin__gt=hora,
            activo=True
        ).first()
        
        if not disponibilidad:
            return False
        
        # Calcular la duración del servicio en minutos
        duracion_servicio = servicio.duracion_minutos
        
        # Calcular la hora de finalización del servicio
        hora_fin_servicio = (fecha_hora + timezone.timedelta(minutes=duracion_servicio)).time()
        
        # Verificar que la hora de finalización esté dentro del horario disponible
        if hora_fin_servicio > disponibilidad.hora_fin:
            return False
        
        # Contar cuántas reservas hay para esa fecha y hora
        reservas_existentes = Reserva.objects.filter(
            fecha_hora=fecha_hora,
            estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
        ).count()
        
        # Verificar si hay capacidad disponible
        return reservas_existentes < disponibilidad.capacidad_maxima


class Vehiculo(models.Model):
    """
    Modelo para almacenar la información de los vehículos de los clientes.
    """
    # Tipos de vehículo
    AUTOMOVIL = 'AU'
    CAMIONETA = 'CA'
    SUV = 'SU'
    MOTOCICLETA = 'MO'
    OTRO = 'OT'
    
    TIPO_CHOICES = [
        (AUTOMOVIL, _('Automóvil')),
        (CAMIONETA, _('Camioneta')),
        (SUV, _('SUV')),
        (MOTOCICLETA, _('Motocicleta')),
        (OTRO, _('Otro')),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='vehiculos', verbose_name=_('Cliente'))
    tipo = models.CharField(max_length=2, choices=TIPO_CHOICES, default=AUTOMOVIL, verbose_name=_('Tipo'))
    marca = models.CharField(max_length=50, verbose_name=_('Marca'))
    modelo = models.CharField(max_length=50, verbose_name=_('Modelo'))
    anio = models.PositiveIntegerField(verbose_name=_('Año'))
    placa = models.CharField(max_length=10, verbose_name=_('Placa'))
    color = models.CharField(max_length=30, verbose_name=_('Color'))
    observaciones = models.TextField(blank=True, verbose_name=_('Observaciones'))
    
    class Meta:
        verbose_name = _('Vehículo')
        verbose_name_plural = _('Vehículos')
        ordering = ['cliente', 'marca', 'modelo']
    
    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.placa})"


class HorarioDisponible(models.Model):
    """
    Modelo para almacenar los horarios disponibles específicos para reservas.
    """
    fecha = models.DateField(verbose_name=_('Fecha'))
    hora_inicio = models.TimeField(verbose_name=_('Hora de Inicio'))
    hora_fin = models.TimeField(verbose_name=_('Hora de Fin'))
    disponible = models.BooleanField(default=True, verbose_name=_('Disponible'))
    capacidad = models.PositiveSmallIntegerField(default=1, verbose_name=_('Capacidad'))
    reservas_actuales = models.PositiveSmallIntegerField(default=0, verbose_name=_('Reservas Actuales'))
    
    class Meta:
        verbose_name = _('Horario Disponible')
        verbose_name_plural = _('Horarios Disponibles')
        ordering = ['fecha', 'hora_inicio']
        unique_together = ['fecha', 'hora_inicio', 'hora_fin']
    
    def __str__(self):
        return f"{self.fecha.strftime('%d/%m/%Y')} - {self.hora_inicio.strftime('%H:%M')} a {self.hora_fin.strftime('%H:%M')}"
    
    @property
    def esta_lleno(self):
        return self.reservas_actuales >= self.capacidad
    
    def incrementar_reservas(self):
        if not self.esta_lleno:
            self.reservas_actuales += 1
            self.save(update_fields=['reservas_actuales'])
            return True
        return False
    
    def decrementar_reservas(self):
        if self.reservas_actuales > 0:
            self.reservas_actuales -= 1
            self.save(update_fields=['reservas_actuales'])
            return True
        return False
