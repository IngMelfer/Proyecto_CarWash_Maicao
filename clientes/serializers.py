from rest_framework import serializers
from .models import Cliente, HistorialServicio

class ClienteSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Cliente"""
    nombre_completo = serializers.SerializerMethodField()
    tipo_documento_display = serializers.CharField(source='get_tipo_documento_display', read_only=True)
    
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'apellido', 'nombre_completo', 'email', 'tipo_documento', 
                 'tipo_documento_display', 'numero_documento', 'telefono', 'direccion', 
                 'ciudad', 'fecha_nacimiento', 'saldo_puntos', 'recibir_notificaciones']
        read_only_fields = ['saldo_puntos']
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido}"


class HistorialServicioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo HistorialServicio"""
    cliente = ClienteSerializer(read_only=True)
    
    class Meta:
        model = HistorialServicio
        fields = ['id', 'cliente', 'servicio', 'descripcion', 'fecha_servicio', 
                 'monto', 'puntos_ganados', 'comentarios']
        read_only_fields = ['cliente']