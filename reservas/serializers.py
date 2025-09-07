from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import Servicio, Reserva, Vehiculo, HorarioDisponible, Bahia
from clientes.models import Cliente
from clientes.serializers import ClienteSerializer

class ServicioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Servicio"""
    class Meta:
        model = Servicio
        fields = ['id', 'nombre', 'descripcion', 'precio', 'duracion_minutos', 'puntos_otorgados', 'activo']


class ReservaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Reserva"""
    cliente = ClienteSerializer(read_only=True)
    servicio = ServicioSerializer(read_only=True)
    servicio_id = serializers.PrimaryKeyRelatedField(
        queryset=Servicio.objects.filter(activo=True),
        write_only=True,
        source='servicio'
    )
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Reserva
        fields = ['id', 'cliente', 'servicio', 'servicio_id', 'fecha_hora', 'estado', 
                 'estado_display', 'bahia', 'notas', 'fecha_creacion', 'fecha_actualizacion']
        read_only_fields = ['estado', 'bahia', 'fecha_creacion', 'fecha_actualizacion']
    
    def validate_fecha_hora(self, value):
        """Validar que la fecha y hora de la reserva sea futura"""
        # Verificar que la fecha sea futura
        if value <= timezone.now():
            raise serializers.ValidationError(_('La fecha y hora de la reserva debe ser futura'))
        
        # Verificar que la fecha sea en horario de atención (8am a 6pm)
        if value.hour < 8 or value.hour >= 18:
            raise serializers.ValidationError(_('El horario de atención es de 8:00 AM a 6:00 PM'))
        
        # Verificar que no sea domingo (día 6 en Python)
        if value.weekday() == 6:
            raise serializers.ValidationError(_('No se atiende los domingos'))
        
        return value
    
    def validate(self, data):
        """Validar que no haya otra reserva para el mismo servicio y hora"""
        servicio = data.get('servicio')
        fecha_hora = data.get('fecha_hora')
        
        # Verificar disponibilidad
        if servicio and fecha_hora:
            # Calcular la hora de finalización basada en la duración del servicio
            duracion = timezone.timedelta(minutes=servicio.duracion_minutos)
            hora_fin = fecha_hora + duracion
            
            # Verificar que no haya otra reserva para el mismo servicio y hora
            reservas_existentes = Reserva.objects.filter(
                servicio=servicio,
                fecha_hora__lt=hora_fin,
                fecha_hora__gt=fecha_hora - duracion,
                estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
            )
            
            if self.instance:
                reservas_existentes = reservas_existentes.exclude(id=self.instance.id)
            
            if reservas_existentes.exists():
                raise serializers.ValidationError(_('Ya existe una reserva para este servicio en el horario seleccionado'))
        
        return data


# Esta clase se ha movido más abajo


class VehiculoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Vehiculo"""
    cliente = ClienteSerializer(read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Vehiculo
        fields = ['id', 'cliente', 'tipo', 'tipo_display', 'marca', 'modelo', 'anio', 'placa', 'color', 'observaciones']
        read_only_fields = ['cliente']
    
    def validate_placa(self, value):
        """Validar que la placa sea única para el cliente"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and hasattr(request.user, 'cliente'):
            cliente = request.user.cliente
            # Verificar si ya existe un vehículo con la misma placa para este cliente
            if Vehiculo.objects.filter(cliente=cliente, placa=value).exclude(id=self.instance.id if self.instance else None).exists():
                raise serializers.ValidationError(_('Ya tienes un vehículo registrado con esta placa'))
        return value


class BahiaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Bahia"""
    codigo_qr_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Bahia
        fields = ['id', 'nombre', 'descripcion', 'activo', 'tiene_camara', 'ip_camara', 'codigo_qr', 'codigo_qr_url']
    
    def get_codigo_qr_url(self, obj):
        """Retorna la URL del código QR si existe"""
        if obj.codigo_qr:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.codigo_qr.url)
        return None


class HorarioDisponibleSerializer(serializers.ModelSerializer):
    """Serializer para el modelo HorarioDisponible"""
    class Meta:
        model = HorarioDisponible
        fields = ['id', 'fecha', 'hora_inicio', 'hora_fin', 'disponible', 'capacidad', 'reservas_actuales', 'esta_lleno']


class ReservaUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar el estado de una reserva"""
    class Meta:
        model = Reserva
        fields = ['estado', 'notas']
    
    def validate_estado(self, value):
        """Validar que el cambio de estado sea válido"""
        if not self.instance:
            return value
        
        estado_actual = self.instance.estado
        
        # Validar transiciones de estado permitidas
        if estado_actual == Reserva.PENDIENTE and value not in [Reserva.CONFIRMADA, Reserva.CANCELADA]:
            raise serializers.ValidationError(_('Desde estado Pendiente solo puede pasar a Confirmada o Cancelada'))
        
        if estado_actual == Reserva.CONFIRMADA and value not in [Reserva.EN_PROCESO, Reserva.CANCELADA]:
            raise serializers.ValidationError(_('Desde estado Confirmada solo puede pasar a En Proceso o Cancelada'))
        
        if estado_actual == Reserva.EN_PROCESO and value != Reserva.COMPLETADA:
            raise serializers.ValidationError(_('Desde estado En Proceso solo puede pasar a Completada'))
        
        if estado_actual in [Reserva.COMPLETADA, Reserva.CANCELADA]:
            raise serializers.ValidationError(_('No se puede cambiar el estado de una reserva Completada o Cancelada'))
        
        return value