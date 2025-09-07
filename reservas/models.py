from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from clientes.models import Cliente
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class MedioPago(models.Model):
    """
    Modelo para almacenar los diferentes medios de pago disponibles.
    """
    # Tipos básicos de pago
    EFECTIVO = 'EF'
    TARJETA = 'TA'
    TRANSFERENCIA = 'TR'
    PUNTOS = 'PU'
    
    # Pasarelas de pago colombianas
    WOMPI = 'WO'
    PAYU = 'PY'
    EPAYCO = 'EP'
    NEQUI = 'NQ'
    PSE = 'PS'
    
    TIPO_CHOICES = [
        (EFECTIVO, _('Efectivo')),
        (TARJETA, _('Tarjeta')),
        (TRANSFERENCIA, _('Transferencia')),
        (PUNTOS, _('Puntos')),
        (WOMPI, _('Wompi')),
        (PAYU, _('PayU')),
        (EPAYCO, _('ePayco')),
        (NEQUI, _('Nequi')),
        (PSE, _('PSE')),
    ]
    
    tipo = models.CharField(max_length=2, choices=TIPO_CHOICES, default=EFECTIVO, verbose_name=_('Tipo'))
    nombre = models.CharField(max_length=50, verbose_name=_('Nombre'))
    descripcion = models.TextField(blank=True, verbose_name=_('Descripción'))
    activo = models.BooleanField(default=True, verbose_name=_('Activo'))
    api_key = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('API Key'))
    api_secret = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('API Secret'))
    merchant_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('ID de Comercio'))
    sandbox = models.BooleanField(default=True, verbose_name=_('Modo Sandbox'))
    
    class Meta:
        verbose_name = _('Medio de Pago')
        verbose_name_plural = _('Medios de Pago')
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
        
    def es_pasarela(self):
        """
        Determina si el medio de pago es una pasarela de pago en línea.
        """
        return self.tipo in [self.WOMPI, self.PAYU, self.EPAYCO, self.NEQUI, self.PSE]
        
    def get_config(self):
        """
        Retorna la configuración necesaria para la pasarela de pago.
        """
        if not self.es_pasarela():
            return None
            
        config = {
            'tipo': self.get_tipo_display(),
            'api_key': self.api_key,
            'sandbox': self.sandbox,
        }
        
        if self.tipo in [self.WOMPI, self.PAYU, self.EPAYCO]:
            config['api_secret'] = self.api_secret
            
        if self.tipo in [self.PAYU, self.EPAYCO]:
            config['merchant_id'] = self.merchant_id
            
        return config


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
    bahia = models.ForeignKey('Bahia', on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas', verbose_name=_('Bahía'))
    estado = models.CharField(max_length=2, choices=ESTADO_CHOICES, default=PENDIENTE, verbose_name=_('Estado'))
    notas = models.TextField(blank=True, verbose_name=_('Notas'))
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Creación'))
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name=_('Última Actualización'))
    medio_pago = models.ForeignKey(MedioPago, on_delete=models.PROTECT, null=True, blank=True, related_name='reservas', verbose_name=_('Medio de Pago'))
    stream_token = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('Token de Transmisión'))
    referencia_pago = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Referencia de Pago'), help_text=_('Referencia única para el pago en pasarelas'))
    
    class Meta:
        verbose_name = _('Reserva')
        verbose_name_plural = _('Reservas')
        ordering = ['-fecha_hora']
        # Evitar reservas duplicadas para el mismo servicio, hora y bahía
        constraints = [
            models.UniqueConstraint(fields=['fecha_hora', 'bahia'], name='unique_reserva_bahia')
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
        Si la bahía tiene cámara, genera un código QR para ver el lavado en vivo.
        """
        if self.estado == self.PENDIENTE:
            self.estado = self.CONFIRMADA
            self.save(update_fields=['estado', 'fecha_actualizacion'])
            
            # Si la bahía tiene cámara, generar código QR para esta reserva
            if self.bahia and self.bahia.tiene_camara and self.bahia.ip_camara:
                import qrcode
                import os
                from django.conf import settings
                from io import BytesIO
                from django.core.files import File
                
                # Crear el QR con la URL para ver la cámara de esta reserva
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                
                # La URL incluirá el ID de la reserva para validar acceso
                url = f"/reservas/ver-camara/{self.id}/"
                qr.add_data(url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Guardar la imagen como archivo
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                file_name = f'reserva_{self.id}_qr.png'
                
                # Guardar el archivo en el campo codigo_qr de la bahía
                self.bahia.codigo_qr.save(file_name, File(buffer), save=True)
            
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
        Libera la bahía ocupada.
        Elimina el código QR si existe.
        """
        if self.estado == self.EN_PROCESO:
            self.estado = self.COMPLETADA
            
            # Liberar la bahía y eliminar el código QR
            if self.bahia:
                # Si la bahía tiene un código QR, eliminarlo
                if self.bahia.codigo_qr:
                    self.bahia.codigo_qr.delete(save=False)
                    self.bahia.save(update_fields=['codigo_qr'])
                # La bahía queda disponible para nuevas reservas
                # No es necesario hacer nada más ya que al cambiar el estado
                # la bahía ya no se considera ocupada para ese horario
            
            self.save(update_fields=['estado'])
            
            # Acumular puntos al cliente
            self.cliente.acumular_puntos(self.servicio.puntos_otorgados)
            
            # Decrementar contador de reservas en el horario si existe
            horario = HorarioDisponible.objects.filter(
                fecha=self.fecha_hora.date(),
                hora_inicio__lte=self.fecha_hora.time(),
                hora_fin__gt=self.fecha_hora.time()
            ).first()
            
            if horario:
                horario.decrementar_reservas()
            
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


class Bahia(models.Model):
    """
    Modelo para representar las bahías (lugares físicos) donde se realizan los servicios.
    """
    nombre = models.CharField(max_length=50, verbose_name=_('Nombre'))
    descripcion = models.TextField(blank=True, verbose_name=_('Descripción'))
    activo = models.BooleanField(default=True, verbose_name=_('Activo'))
    tiene_camara = models.BooleanField(default=False, verbose_name=_('Tiene Cámara Web'))
    ip_camara = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('IP de la Cámara'))
    codigo_qr = models.ImageField(upload_to='bahias/qr/', blank=True, null=True, verbose_name=_('Código QR'))
    
    class Meta:
        verbose_name = _('Bahía')
        verbose_name_plural = _('Bahías')
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
        
    def save(self, *args, **kwargs):
        """Sobrescribir el método save para generar el código QR si tiene cámara y una IP asignada"""
        # Primero guardamos el objeto para asegurar que tenga un ID
        super().save(*args, **kwargs)
        
        # Si tiene cámara y una IP asignada, generamos el código QR
        if self.tiene_camara and self.ip_camara:
            import qrcode
            import os
            from django.conf import settings
            from io import BytesIO
            from django.core.files import File
            
            # Crear el QR con la URL de la cámara
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(f"http://{self.ip_camara}")
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Guardar la imagen como archivo
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            file_name = f'bahia_{self.id}_qr.png'
            
            # Guardar el archivo en el campo codigo_qr
            self.codigo_qr.save(file_name, File(buffer), save=False)
            
            # Guardar el objeto sin llamar al método save de nuevo para evitar recursión
            super().save(update_fields=['codigo_qr'])


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
