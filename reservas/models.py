from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime, timedelta
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
    
    # Lista de medios de pago electrónicos
    MEDIOS_ELECTRONICOS = ['TA', 'WO', 'PY', 'EP', 'NQ', 'PS']
    
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
    
    # Campos adicionales para configuraciones específicas
    client_id = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Client ID'))
    client_secret = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Client Secret'))
    public_key = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Public Key'))
    account_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Account ID'))
    base_url = models.URLField(blank=True, null=True, verbose_name=_('URL Base'))
    webhook_url = models.URLField(blank=True, null=True, verbose_name=_('URL Webhook'))
    
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
        
    def es_puntos(self):
        """
        Determina si el medio de pago es con puntos.
        """
        return self.tipo == self.PUNTOS
        
    def es_electronico(self):
        """
        Determina si el medio de pago es electrónico (tarjeta o pasarela)
        """
        return self.tipo in MedioPago.MEDIOS_ELECTRONICOS
        
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
        
        # Configuraciones específicas por tipo de pasarela
        if self.tipo == self.NEQUI:
            config.update({
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'base_url': self.base_url or 'https://api.nequi.com.co',
                'webhook_url': self.webhook_url,
            })
        elif self.tipo == self.WOMPI:
            config.update({
                'public_key': self.public_key,
                'api_secret': self.api_secret,
                'webhook_url': self.webhook_url,
            })
        elif self.tipo == self.PAYU:
            config.update({
                'api_secret': self.api_secret,
                'merchant_id': self.merchant_id,
                'account_id': self.account_id,
                'webhook_url': self.webhook_url,
            })
        elif self.tipo == self.EPAYCO:
            config.update({
                'api_secret': self.api_secret,
                'merchant_id': self.merchant_id,
                'public_key': self.public_key,
                'webhook_url': self.webhook_url,
            })
        elif self.tipo == self.PSE:
            # PSE generalmente usa PayU como procesador
            config.update({
                'api_secret': self.api_secret,
                'merchant_id': self.merchant_id,
                'account_id': self.account_id,
                'webhook_url': self.webhook_url,
            })
            
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
    INCUMPLIDA = 'IN'
    
    ESTADO_CHOICES = [
        (PENDIENTE, _('Pendiente')),
        (CONFIRMADA, _('Confirmada')),
        (EN_PROCESO, _('En Proceso')),
        (COMPLETADA, _('Completada')),
        (CANCELADA, _('Cancelada')),
        (INCUMPLIDA, _('Incumplida')),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='reservas', verbose_name=_('Cliente'))
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='reservas', verbose_name=_('Servicio'))
    fecha_hora = models.DateTimeField(verbose_name=_('Fecha y Hora'))
    bahia = models.ForeignKey('Bahia', on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas', verbose_name=_('Bahía'))
    vehiculo = models.ForeignKey('Vehiculo', on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas', verbose_name=_('Vehículo'))
    lavador = models.ForeignKey('empleados.Empleado', on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas_asignadas', verbose_name=_('Lavador'))
    asignacion_automatica = models.BooleanField(default=True, verbose_name=_('Asignación Automática'), help_text=_('Indica si el lavador fue asignado automáticamente o seleccionado por el cliente'))
    estado = models.CharField(max_length=2, choices=ESTADO_CHOICES, default=PENDIENTE, verbose_name=_('Estado'))
    notas = models.TextField(blank=True, verbose_name=_('Notas'))
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Creación'))
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name=_('Última Actualización'))
    fecha_inicio_servicio = models.DateTimeField(null=True, blank=True, verbose_name=_('Fecha de Inicio del Servicio'))
    medio_pago = models.ForeignKey(MedioPago, on_delete=models.PROTECT, null=True, blank=True, related_name='reservas', verbose_name=_('Medio de Pago'))
    precio_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Precio Final'))
    descuento_aplicado = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('Descuento Aplicado'))
    puntos_redimidos = models.PositiveIntegerField(default=0, verbose_name=_('Puntos Redimidos'))
    recompensa_aplicada = models.CharField(max_length=100, blank=True, verbose_name=_('Recompensa Aplicada'))
    stream_token = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('Token de Transmisión'))
    referencia_pago = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Referencia de Pago'), help_text=_('Referencia única para el pago en pasarelas'))
    puntos_redimidos = models.PositiveIntegerField(default=0, verbose_name=_('Puntos Redimidos'), help_text=_('Cantidad de puntos redimidos para esta reserva'))
    descuento_aplicado = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('Descuento Aplicado'), help_text=_('Monto de descuento aplicado por redención de puntos'))
    fecha_confirmacion = models.DateTimeField(null=True, blank=True, verbose_name=_('Fecha de Confirmación'))
    calificacion_solicitada = models.BooleanField(default=False, verbose_name=_('Calificación Solicitada'), help_text=_('Indica si se ha enviado la solicitud de calificación al cliente'))
    
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
            self.fecha_confirmacion = timezone.now()
            self.save(update_fields=['estado', 'fecha_actualizacion', 'fecha_confirmacion'])
            
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
                
                buffer = BytesIO()
                img.save(buffer, format='PNG')
                file_name = f'reserva_{self.id}_qr.png'
                
                # Guardar el archivo en el campo codigo_qr de la bahía
                self.bahia.codigo_qr.save(file_name, File(buffer), save=True)
            
            return True
        return False
    
    def asignar_lavador(self, lavador=None, automatico=True):
        """
        Asigna un lavador a la reserva. Si no se especifica un lavador,
        se asigna automáticamente uno disponible que no tenga conflictos de horario.
        """
        from empleados.models import Empleado
        from datetime import datetime, timedelta
        
        if lavador:
            self.lavador = lavador
            self.asignacion_automatica = False
        else:
            # Buscar lavadores disponibles
            lavadores_base = Empleado.objects.filter(
                rol=Empleado.ROL_LAVADOR,
                disponible=True,
                activo=True
            )
            
            # Filtrar lavadores que no tengan conflictos de horario
            lavadores_sin_conflicto = []
            
            for lavador_candidato in lavadores_base:
                # Calcular duración del servicio actual
                duracion_servicio = 1  # Por defecto 1 hora
                if self.servicio:
                    duracion_servicio = (self.servicio.duracion_minutos + 59) // 60
                
                # Calcular hora de fin de la nueva reserva
                hora_fin_nueva = self.fecha_hora + timedelta(hours=duracion_servicio)
                
                # Verificar si el lavador tiene conflictos
                reservas_conflicto = Reserva.objects.filter(
                    lavador=lavador_candidato,
                    fecha_hora__date=self.fecha_hora.date(),
                    estado__in=[self.PENDIENTE, self.CONFIRMADA, self.EN_PROCESO]
                ).exclude(id=self.id)  # Excluir la reserva actual
                
                tiene_conflicto = False
                for reserva_existente in reservas_conflicto:
                    # Calcular hora de fin de la reserva existente
                    duracion_existente = 1  # Por defecto 1 hora
                    if reserva_existente.servicio:
                        duracion_existente = (reserva_existente.servicio.duracion_minutos + 59) // 60
                    
                    hora_fin_existente = reserva_existente.fecha_hora + timedelta(hours=duracion_existente)
                    
                    # Verificar solapamiento
                    if (self.fecha_hora < hora_fin_existente and hora_fin_nueva > reserva_existente.fecha_hora):
                        tiene_conflicto = True
                        break
                
                if not tiene_conflicto:
                    lavadores_sin_conflicto.append(lavador_candidato)
            
            if lavadores_sin_conflicto:
                # Asignar el lavador con menos reservas pendientes
                lavador_asignado = sorted(
                    lavadores_sin_conflicto,
                    key=lambda l: l.reservas_asignadas.filter(
                        estado__in=[self.PENDIENTE, self.CONFIRMADA, self.EN_PROCESO]
                    ).count()
                )[0]
                
                self.lavador = lavador_asignado
                self.asignacion_automatica = True
            else:
                # No hay lavadores disponibles sin conflictos
                raise ValueError("No hay lavadores disponibles para este horario")
        
        self.save(update_fields=['lavador', 'asignacion_automatica'])
        return self.lavador
    
    def solicitar_calificacion(self):
        """
        Marca la reserva para solicitar calificación al cliente
        """
        if self.estado == self.COMPLETADA and self.lavador and not self.calificacion_solicitada:
            self.calificacion_solicitada = True
            self.save(update_fields=['calificacion_solicitada'])
            return True
        return False
    
    def completar_servicio(self):
        """
        Completa el servicio y solicita calificación
        """
        if self.estado == self.EN_PROCESO:
            self.estado = self.COMPLETADA
            self.save(update_fields=['estado'])
            self.solicitar_calificacion()
            return True
        return False
    
    def iniciar_servicio(self):
        """
        Inicia el servicio si la reserva está confirmada.
        """
        if self.estado == self.CONFIRMADA:
            self.estado = self.EN_PROCESO
            self.fecha_inicio_servicio = timezone.now()
            self.save(update_fields=['estado', 'fecha_inicio_servicio'])
            return True
        return False
    

    
    def completar_servicio(self):
        """
        Completa el servicio si está en proceso.
        Acumula los puntos al cliente.
        Libera la bahía ocupada.
        Elimina el código QR si existe.
        Busca la siguiente reserva pendiente para esa bahía y la asigna automáticamente.
        Crea un registro en el historial de servicios del cliente.
        Crea una notificación para que el cliente califique al lavador.
        """
        if self.estado == self.EN_PROCESO:
            self.estado = self.COMPLETADA
            
            # Guardar la bahía antes de liberarla para buscar la siguiente reserva
            bahia_actual = self.bahia
            
            # Liberar la bahía y eliminar el código QR
            if bahia_actual:
                # Si la bahía tiene un código QR, eliminarlo
                if bahia_actual.codigo_qr:
                    bahia_actual.codigo_qr.delete(save=False)
                    bahia_actual.save(update_fields=['codigo_qr'])
                # La bahía queda disponible para nuevas reservas
                # No es necesario hacer nada más ya que al cambiar el estado
                # la bahía ya no se considera ocupada para ese horario
            
            self.save(update_fields=['estado'])
            
            # Crear registro en historial de servicios
            from clientes.models import HistorialServicio
            from django.utils import timezone
            
            HistorialServicio.objects.create(
                cliente=self.cliente,
                servicio=self.servicio.nombre,
                descripcion=self.servicio.descripcion,
                fecha_servicio=timezone.now(),
                monto=self.servicio.precio,
                puntos_ganados=self.servicio.puntos_otorgados,
                comentarios=self.notas
            )
            
            # Acumular puntos al cliente
            self.cliente.acumular_puntos(self.servicio.puntos_otorgados)
            
            # Crear notificación para calificar al lavador
            if self.lavador:
                from notificaciones.models import Notificacion
                from django.urls import reverse
                
                # Crear URL para calificar al lavador
                url_calificacion = reverse('reservas:calificar_lavador', kwargs={'reserva_id': self.id})
                
                mensaje = f"""¡Tu servicio de <strong>{self.servicio.nombre}</strong> ha sido completado exitosamente!
                
Tu lavador <strong>{self.lavador.usuario.get_full_name()}</strong> ha terminado el servicio. 
¿Qué tal estuvo? Tu opinión es muy importante para nosotros.

<div class="mt-3 mb-3">
    <a href="{url_calificacion}" class="btn btn-primary btn-sm">
        <i class="fas fa-star me-1"></i>Haz clic aquí para calificar el servicio
    </a>
</div>

¡Gracias por confiar en nosotros!"""
                
                Notificacion.objects.create(
                    cliente=self.cliente,
                    reserva=self,
                    tipo=Notificacion.SERVICIO_FINALIZADO,
                    titulo=f'Servicio completado - ¡Califica tu experiencia!',
                    mensaje=mensaje
                )
            
            # Decrementar contador de reservas en el horario si existe
            horario = HorarioDisponible.objects.filter(
                fecha=self.fecha_hora.date(),
                hora_inicio__lte=self.fecha_hora.time(),
                hora_fin__gt=self.fecha_hora.time()
            ).first()
            
            if horario:
                horario.decrementar_reservas()
            
            # Buscar la siguiente reserva pendiente para esta bahía
            if bahia_actual:
                from django.utils import timezone
                # Buscar la siguiente reserva pendiente más cercana en el tiempo para esta bahía
                siguiente_reserva = Reserva.objects.filter(
                    bahia=bahia_actual,
                    estado=Reserva.PENDIENTE,
                    fecha_hora__gte=timezone.now()
                ).order_by('fecha_hora').first()
                
                # Si hay una siguiente reserva pendiente, confirmarla automáticamente
                if siguiente_reserva:
                    siguiente_reserva.confirmar()
            
            return True
        return False


class DisponibilidadHoraria(models.Model):
    """
    Modelo para gestionar la disponibilidad horaria del autolavado.
    
    Este modelo define los horarios disponibles para cada día de la semana.
    - El campo 'activo' permite activar o desactivar completamente un horario específico.
    - La 'capacidad_maxima' representa el número máximo de vehículos que pueden ser atendidos
      simultáneamente en este horario (relacionado con el número de bahías disponibles).
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
    capacidad_maxima = models.PositiveSmallIntegerField(default=1, verbose_name=_('Capacidad Máxima'), 
                                                      help_text=_('Número máximo de vehículos que pueden ser atendidos simultáneamente en este horario'))
    activo = models.BooleanField(default=True, verbose_name=_('Activo'), 
                               help_text=_('Indica si este horario está disponible para reservas'))
    
    class Meta:
        verbose_name = _('Disponibilidad Horaria')
        verbose_name_plural = _('Disponibilidades Horarias')
        ordering = ['dia_semana', 'hora_inicio']
    
    def __str__(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"{self.get_dia_semana_display()} - {self.hora_inicio} a {self.hora_fin} ({estado})"
        
    @property
    def esta_disponible(self):
        """Indica si este horario está disponible para reservas."""
        return self.activo
    
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
        hora_fin_servicio = (fecha_hora + timedelta(minutes=duracion_servicio)).time()
        
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
        # La placa debe ser única en todo el sistema
        constraints = [
            models.UniqueConstraint(fields=['placa'], name='unique_placa_vehiculo')
        ]
    
    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.placa})"


class Bahia(models.Model):
    """
    Modelo para representar las bahías (lugares físicos) donde se realizan los servicios.
    """
    # Opciones para el tipo de cámara
    TIPO_CAMARA_CHOICES = [
        ('droidcam', 'DroidCam'),
        ('ipwebcam', 'IP Webcam'),
        ('iriun', 'Iriun Webcam'),
        ('rtsp', 'Cámara RTSP'),
        ('http', 'Cámara HTTP'),
        ('otro', 'Otro tipo de cámara'),
    ]
    
    nombre = models.CharField(max_length=50, verbose_name=_('Nombre'))
    descripcion = models.TextField(blank=True, verbose_name=_('Descripción'))
    activo = models.BooleanField(default=True, verbose_name=_('Activo'))
    tiene_camara = models.BooleanField(default=False, verbose_name=_('Tiene Cámara Web'))
    tipo_camara = models.CharField(max_length=20, choices=TIPO_CAMARA_CHOICES, default='ipwebcam', blank=True, null=True, verbose_name=_('Tipo de Cámara'))
    ip_camara = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('URL/IP de la Cámara'))
    
    # Campos adicionales para configuración en producción
    ip_publica = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('IP Pública/Dominio'), help_text=_('IP pública o dominio para acceso desde internet'))
    puerto_externo = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('Puerto Externo'), help_text=_('Puerto configurado en el router para acceso externo'))
    usuario_camara = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('Usuario de la Cámara'), help_text=_('Usuario para autenticación (si es requerido)'))
    password_camara = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Contraseña de la Cámara'), help_text=_('Contraseña para autenticación (si es requerido)'))
    usar_ssl = models.BooleanField(default=False, verbose_name=_('Usar HTTPS/SSL'), help_text=_('Marcar si la cámara usa conexión segura'))
    activa_produccion = models.BooleanField(default=False, verbose_name=_('Activa en Producción'), help_text=_('Usar configuración de producción (IP pública) en lugar de local'))
    
    codigo_qr = models.ImageField(upload_to='bahias/qr/', blank=True, null=True, verbose_name=_('Código QR'))
    
    class Meta:
        verbose_name = _('Bahía')
        verbose_name_plural = _('Bahías')
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
        
    def get_camera_url(self):
        """Obtiene la URL completa de la cámara según su tipo y configuración"""
        if not self.tiene_camara or not self.ip_camara:
            return None
        
        # Determinar qué IP usar según la configuración
        if self.activa_produccion and self.ip_publica:
            # Usar configuración de producción
            base_ip = self.ip_publica
            puerto = self.puerto_externo if self.puerto_externo else 8080
        else:
            # Usar configuración local
            base_ip = self.ip_camara
            puerto = None
            
        # Si la URL ya incluye protocolo, usarla directamente
        if base_ip.startswith(('http://', 'https://', 'rtsp://')): 
            return base_ip
            
        # Determinar protocolo
        protocolo = 'https' if self.usar_ssl else 'http'
        
        # Construir URL con autenticación si es necesaria
        auth_string = ""
        if self.usuario_camara and self.password_camara:
            auth_string = f"{self.usuario_camara}:{self.password_camara}@"
            
        # Generar URL según el tipo de cámara
        if self.tipo_camara == 'droidcam':
            # DroidCam usa el formato http://IP:PUERTO/video
            if puerto:
                return f"{protocolo}://{auth_string}{base_ip}:{puerto}/video"
            elif '/video' in base_ip:
                return f"{protocolo}://{auth_string}{base_ip}"
            else:
                return f"{protocolo}://{auth_string}{base_ip}/video"
                
        elif self.tipo_camara == 'ipwebcam':
            # IP Webcam usa el formato http://IP:PUERTO/video
            if puerto:
                return f"{protocolo}://{auth_string}{base_ip}:{puerto}/video"
            elif '/video' in base_ip:
                return f"{protocolo}://{auth_string}{base_ip}"
            else:
                return f"{protocolo}://{auth_string}{base_ip}/video"
                
        elif self.tipo_camara == 'iriun':
            # Iriun Webcam - usar la URL proporcionada
            if puerto:
                return f"{protocolo}://{auth_string}{base_ip}:{puerto}"
            else:
                return f"{protocolo}://{auth_string}{base_ip}"
                
        elif self.tipo_camara == 'rtsp':
            # Cámaras RTSP
            if puerto:
                return f"rtsp://{auth_string}{base_ip}:{puerto}"
            else:
                return f"rtsp://{auth_string}{base_ip}"
                
        else:  # http y otros tipos
            # Para cámaras HTTP genéricas
            if puerto:
                return f"{protocolo}://{auth_string}{base_ip}:{puerto}"
            else:
                return f"{protocolo}://{auth_string}{base_ip}"
    
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
            
            # Obtener la URL completa de la cámara
            camera_url = self.get_camera_url()
            qr.add_data(camera_url)
                
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


# Se eliminó el modelo FechaEspecial


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
