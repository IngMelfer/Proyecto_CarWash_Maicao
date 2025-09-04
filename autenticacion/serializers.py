from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from clientes.models import Cliente

Usuario = get_user_model()

class RegistroUsuarioSerializer(serializers.ModelSerializer):
    """Serializer para el registro de nuevos usuarios"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    # Campos del cliente
    nombre = serializers.CharField(required=True)
    apellido = serializers.CharField(required=True)
    tipo_documento = serializers.ChoiceField(choices=Cliente.TIPO_DOCUMENTO_CHOICES, required=True)
    numero_documento = serializers.CharField(required=True)
    telefono = serializers.CharField(required=True)
    direccion = serializers.CharField(required=True)
    ciudad = serializers.CharField(required=True)
    fecha_nacimiento = serializers.DateField(required=False)
    recibir_notificaciones = serializers.BooleanField(default=True)
    
    class Meta:
        model = Usuario
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name',
                 'nombre', 'apellido', 'tipo_documento', 'numero_documento',
                 'telefono', 'direccion', 'ciudad', 'fecha_nacimiento',
                 'recibir_notificaciones']
    
    def validate(self, data):
        # Validar que las contraseñas coincidan
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": _('Las contraseñas no coinciden')})
        
        # Validar que el email no esté registrado
        if Usuario.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": _('Este correo electrónico ya está registrado')})
        
        # Validar que el número de documento no esté registrado
        if Cliente.objects.filter(numero_documento=data['numero_documento']).exists():
            raise serializers.ValidationError({"numero_documento": _('Este número de documento ya está registrado')})
        
        return data
    
    def create(self, validated_data):
        # Extraer datos del cliente
        cliente_data = {
            'nombre': validated_data.pop('nombre'),
            'apellido': validated_data.pop('apellido'),
            'tipo_documento': validated_data.pop('tipo_documento'),
            'numero_documento': validated_data.pop('numero_documento'),
            'telefono': validated_data.pop('telefono'),
            'direccion': validated_data.pop('direccion'),
            'ciudad': validated_data.pop('ciudad'),
            'recibir_notificaciones': validated_data.pop('recibir_notificaciones'),
            'email': validated_data['email'],  # Duplicamos el email para el cliente
        }
        
        if 'fecha_nacimiento' in validated_data:
            cliente_data['fecha_nacimiento'] = validated_data.pop('fecha_nacimiento')
        
        # Eliminar password_confirm
        validated_data.pop('password_confirm')
        
        # Crear usuario
        usuario = Usuario.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        
        # Crear cliente asociado al usuario
        Cliente.objects.create(usuario=usuario, **cliente_data)
        
        return usuario


class LoginSerializer(serializers.Serializer):
    """Serializer para el inicio de sesión"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'})


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para mostrar información del usuario"""
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'first_name', 'last_name', 'is_verified']
        read_only_fields = ['id', 'email', 'is_verified']