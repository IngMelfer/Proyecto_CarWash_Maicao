from rest_framework import serializers
from .models import Empleado, RegistroTiempo, Calificacion, Incentivo

class EmpleadoSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = Empleado
        fields = ['id', 'nombre', 'apellido', 'nombre_completo', 'cargo', 'activo', 
                 'fecha_contratacion', 'calificacion_promedio']
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido}"

class EmpleadoDetalleSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    usuario_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Empleado
        fields = ['id', 'nombre', 'apellido', 'nombre_completo', 'tipo_documento', 
                 'numero_documento', 'telefono', 'direccion', 'ciudad', 
                 'fecha_nacimiento', 'cargo', 'fecha_contratacion', 'activo',
                 'calificacion_promedio', 'usuario_email']
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido}"
    
    def get_usuario_email(self, obj):
        if obj.usuario:
            return obj.usuario.email
        return None

class RegistroTiempoSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.SerializerMethodField()
    servicio_nombre = serializers.SerializerMethodField()
    tipo_registro_display = serializers.SerializerMethodField()
    
    class Meta:
        model = RegistroTiempo
        fields = ['id', 'empleado', 'empleado_nombre', 'tipo_registro', 'tipo_registro_display',
                 'fecha_hora', 'servicio', 'servicio_nombre', 'duracion', 'notas']
    
    def get_empleado_nombre(self, obj):
        return f"{obj.empleado.nombre} {obj.empleado.apellido}"
    
    def get_servicio_nombre(self, obj):
        if obj.servicio:
            return obj.servicio.nombre
        return None
    
    def get_tipo_registro_display(self, obj):
        return obj.get_tipo_registro_display()

class CalificacionSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.SerializerMethodField()
    cliente_nombre = serializers.SerializerMethodField()
    servicio_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Calificacion
        fields = ['id', 'empleado', 'empleado_nombre', 'cliente', 'cliente_nombre',
                 'servicio', 'servicio_nombre', 'puntuacion', 'comentario', 'fecha']
    
    def get_empleado_nombre(self, obj):
        return f"{obj.empleado.nombre} {obj.empleado.apellido}"
    
    def get_cliente_nombre(self, obj):
        if obj.cliente:
            return f"{obj.cliente.nombre} {obj.cliente.apellido}"
        return None
    
    def get_servicio_nombre(self, obj):
        if obj.servicio:
            return obj.servicio.nombre
        return None

class IncentivoSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.SerializerMethodField()
    tipo_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Incentivo
        fields = ['id', 'empleado', 'empleado_nombre', 'tipo', 'tipo_display',
                 'monto', 'descripcion', 'fecha_otorgado']
    
    def get_empleado_nombre(self, obj):
        return f"{obj.empleado.nombre} {obj.empleado.apellido}"
    
    def get_tipo_display(self, obj):
        return obj.get_tipo_display()