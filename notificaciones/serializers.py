from rest_framework import serializers
from .models import Notificacion

class NotificacionSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Notificacion"""
    tipo_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Notificacion
        fields = ['id', 'cliente', 'tipo', 'tipo_display', 'titulo', 'mensaje', 
                  'leida', 'fecha_creacion', 'fecha_lectura']
        read_only_fields = ['cliente', 'tipo', 'titulo', 'mensaje', 'fecha_creacion', 'fecha_lectura']
    
    def get_tipo_display(self, obj):
        """Obtener el nombre del tipo de notificación"""
        return obj.get_tipo_display()