from django import forms
from .models import Bahia, Servicio, MedioPago, DisponibilidadHoraria, Reserva, HorarioDisponible, Recompensa
from clientes.models import Cliente

class BahiaForm(forms.ModelForm):
    class Meta:
        model = Bahia
        fields = ['nombre', 'descripcion', 'activo', 'tiene_camara', 'tipo_camara', 'ip_camara', 
                 'ip_publica', 'puerto_externo', 'usuario_camara', 'password_camara', 'usar_ssl', 'activa_produccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tiene_camara': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tipo_camara': forms.Select(attrs={'class': 'form-select'}),
            'ip_camara': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 192.168.1.100:8080'}),
            'ip_publica': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: mi-dominio.com o 203.0.113.1'}),
            'puerto_externo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 8080'}),
            'usuario_camara': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario (opcional)'}),
            'password_camara': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña (opcional)'}),
            'usar_ssl': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'activa_produccion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar etiquetas y ayudas específicas para los campos de cámara
        self.fields['ip_camara'].help_text = 'IP local de la cámara (ej: 192.168.1.100:8080)'
        self.fields['ip_publica'].help_text = 'IP pública o dominio para acceso desde internet (solo para producción)'
        self.fields['puerto_externo'].help_text = 'Puerto configurado en el router para acceso externo'
        self.fields['usuario_camara'].help_text = 'Usuario para autenticación (si la cámara lo requiere)'
        self.fields['password_camara'].help_text = 'Contraseña para autenticación (si la cámara lo requiere)'
        self.fields['usar_ssl'].help_text = 'Marcar si la cámara usa conexión HTTPS/SSL'
        self.fields['activa_produccion'].help_text = 'Usar configuración de producción (IP pública) en lugar de local'

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'descripcion', 'precio', 'duracion_minutos', 'puntos_otorgados', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'duracion_minutos': forms.NumberInput(attrs={'class': 'form-control', 'min': '5', 'step': '5'}),
            'puntos_otorgados': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class MedioPagoForm(forms.ModelForm):
    class Meta:
        model = MedioPago
        fields = ['tipo', 'nombre', 'descripcion', 'activo', 'api_key', 'api_secret', 'merchant_id', 
                 'client_id', 'client_secret', 'public_key', 'account_id', 'base_url', 'webhook_url', 'sandbox']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'api_key': forms.TextInput(attrs={'class': 'form-control'}),
            'api_secret': forms.TextInput(attrs={'class': 'form-control'}),
            'merchant_id': forms.TextInput(attrs={'class': 'form-control'}),
            'client_id': forms.TextInput(attrs={'class': 'form-control'}),
            'client_secret': forms.TextInput(attrs={'class': 'form-control'}),
            'public_key': forms.TextInput(attrs={'class': 'form-control'}),
            'account_id': forms.TextInput(attrs={'class': 'form-control'}),
            'base_url': forms.URLInput(attrs={'class': 'form-control'}),
            'webhook_url': forms.URLInput(attrs={'class': 'form-control'}),
            'sandbox': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar etiquetas y ayudas específicas
        self.fields['api_key'].help_text = 'Clave API proporcionada por la pasarela de pago'
        self.fields['api_secret'].help_text = 'Clave secreta para autenticación'
        self.fields['merchant_id'].help_text = 'ID del comercio en la pasarela'
        self.fields['client_id'].help_text = 'ID del cliente (requerido para Nequi)'
        self.fields['client_secret'].help_text = 'Secreto del cliente (requerido para Nequi)'
        self.fields['public_key'].help_text = 'Clave pública (requerida para Wompi y ePayco)'
        self.fields['account_id'].help_text = 'ID de la cuenta (requerido para PayU y PSE)'
        self.fields['base_url'].help_text = 'URL base de la API (opcional, se usa valor por defecto si está vacío)'
        self.fields['webhook_url'].help_text = 'URL para recibir notificaciones de la pasarela'
        self.fields['sandbox'].help_text = 'Activar modo de pruebas (sandbox)'

class DisponibilidadHorariaForm(forms.ModelForm):
    class Meta:
        model = DisponibilidadHoraria
        fields = ['dia_semana', 'hora_inicio', 'hora_fin', 'capacidad_maxima', 'activo']
        widgets = {
            'dia_semana': forms.Select(attrs={'class': 'form-select'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'capacidad_maxima': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'capacidad_maxima': 'Número máximo de vehículos que pueden ser atendidos simultáneamente en este horario (relacionado con el número de bahías disponibles).',
            'activo': 'Marque esta casilla para activar este horario y permitir reservas durante este período.',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dia_semana'].label = 'Día de la semana'
        self.fields['hora_inicio'].label = 'Hora de inicio'
        self.fields['hora_fin'].label = 'Hora de fin'
        self.fields['capacidad_maxima'].label = 'Capacidad máxima'
        self.fields['activo'].label = 'Horario activo'


# Se eliminó la clase FechaEspecialForm que hacía referencia al modelo FechaEspecial

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['cliente', 'servicio', 'fecha_hora', 'bahia', 'vehiculo', 'estado', 'notas', 'medio_pago']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'servicio': forms.Select(attrs={'class': 'form-select'}),
            'fecha_hora': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'bahia': forms.Select(attrs={'class': 'form-select'}),
            'vehiculo': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medio_pago': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        """Validación para evitar que un mismo vehículo ocupe más de una bahía en el mismo horario
        y que dos clientes tengan el mismo vehículo asociado."""
        cleaned_data = super().clean()
        vehiculo = cleaned_data.get('vehiculo')
        fecha_hora = cleaned_data.get('fecha_hora')
        cliente = cleaned_data.get('cliente')
        
        if vehiculo and fecha_hora:
            # Verificar si el vehículo ya tiene una reserva en el mismo horario
            # Consideramos reservas pendientes, confirmadas o en proceso
            estados_activos = [Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
            reservas_existentes = Reserva.objects.filter(
                vehiculo=vehiculo,
                fecha_hora=fecha_hora,
                estado__in=estados_activos
            )
            
            # Excluir la reserva actual en caso de edición
            if self.instance.pk:
                reservas_existentes = reservas_existentes.exclude(pk=self.instance.pk)
            
            if reservas_existentes.exists():
                raise forms.ValidationError(
                    "Este vehículo ya tiene una reserva en el mismo horario. "
                    "Un vehículo no puede ocupar más de una bahía simultáneamente."
                )
        
        # Verificar que el vehículo pertenezca al cliente seleccionado
        if vehiculo and cliente and vehiculo.cliente != cliente:
            raise forms.ValidationError(
                "El vehículo seleccionado no pertenece al cliente indicado."
            )
            
        return cleaned_data

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'email', 'tipo_documento', 'numero_documento', 'telefono', 'direccion', 'ciudad', 'fecha_nacimiento', 'recibir_notificaciones']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'recibir_notificaciones': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class HorarioDisponibleForm(forms.ModelForm):
    class Meta:
        model = HorarioDisponible
        fields = ['fecha', 'hora_inicio', 'hora_fin', 'disponible', 'capacidad']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
        help_texts = {
            'capacidad': 'Número máximo de vehículos que pueden ser atendidos simultáneamente en este horario.',
            'disponible': 'Marque esta casilla para activar este horario y permitir reservas durante este período.',
        }

class RecompensaForm(forms.ModelForm):
    class Meta:
        model = Recompensa
        fields = ['nombre', 'descripcion', 'servicio', 'tipo', 'puntos_requeridos', 'valor_porcentaje', 'valor_monto', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'servicio': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'puntos_requeridos': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'valor_porcentaje': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'valor_monto': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'tipo': 'Seleccione el tipo de recompensa: Descuento porcentual, monto fijo, o servicio gratis.',
            'puntos_requeridos': 'Cantidad de puntos que el cliente debe redimir para aplicar esta recompensa.',
            'valor_porcentaje': 'Requerido si el tipo es "Descuento porcentual". Valor entre 0 y 100.',
            'valor_monto': 'Requerido si el tipo es "Descuento por monto". Valor mayor a 0.',
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        valor_porcentaje = cleaned_data.get('valor_porcentaje')
        valor_monto = cleaned_data.get('valor_monto')
        puntos_requeridos = cleaned_data.get('puntos_requeridos')

        # Validación de puntos requeridos
        if puntos_requeridos is None or puntos_requeridos < 0:
            self.add_error('puntos_requeridos', 'Los puntos requeridos deben ser 0 o mayores.')

        # Validación según el tipo de recompensa
        if tipo == Recompensa.TIPO_DESCUENTO_PORCENTAJE:
            if not valor_porcentaje:
                self.add_error('valor_porcentaje', 'Debe especificar un porcentaje para el descuento.')
            else:
                try:
                    if float(valor_porcentaje) <= 0 or float(valor_porcentaje) > 100:
                        self.add_error('valor_porcentaje', 'El porcentaje debe ser mayor a 0 y no exceder 100.')
                except (TypeError, ValueError):
                    self.add_error('valor_porcentaje', 'El porcentaje debe ser un número válido.')
            # Limpiar valor_monto si se ingresó por error
            cleaned_data['valor_monto'] = None

        elif tipo == Recompensa.TIPO_DESCUENTO_MONTO:
            if not valor_monto:
                self.add_error('valor_monto', 'Debe especificar un monto para el descuento.')
            else:
                try:
                    if float(valor_monto) <= 0:
                        self.add_error('valor_monto', 'El monto debe ser mayor a 0.')
                except (TypeError, ValueError):
                    self.add_error('valor_monto', 'El monto debe ser un número válido.')
            # Limpiar valor_porcentaje si se ingresó por error
            cleaned_data['valor_porcentaje'] = None

        elif tipo == Recompensa.TIPO_SERVICIO_GRATIS:
            # Para servicio gratis, no deben establecerse valores de porcentaje ni monto
            cleaned_data['valor_porcentaje'] = None
            cleaned_data['valor_monto'] = None

        else:
            self.add_error('tipo', 'Tipo de recompensa no válido.')

        return cleaned_data