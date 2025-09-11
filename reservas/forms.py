from django import forms
from .models import Bahia, Servicio, MedioPago, DisponibilidadHoraria, Reserva, FechaEspecial
from clientes.models import Cliente

class BahiaForm(forms.ModelForm):
    class Meta:
        model = Bahia
        fields = ['nombre', 'descripcion', 'activo', 'tiene_camara', 'ip_camara']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tiene_camara': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ip_camara': forms.TextInput(attrs={'class': 'form-control'}),
        }

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
        fields = ['tipo', 'nombre', 'descripcion', 'activo', 'api_key', 'api_secret', 'merchant_id', 'sandbox']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'api_key': forms.TextInput(attrs={'class': 'form-control'}),
            'api_secret': forms.TextInput(attrs={'class': 'form-control'}),
            'merchant_id': forms.TextInput(attrs={'class': 'form-control'}),
            'sandbox': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

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


class FechaEspecialForm(forms.ModelForm):
    """Formulario para crear o editar una fecha especial"""
    
    # Campos adicionales para seleccionar horarios predefinidos
    horario_inicio_choices = forms.ChoiceField(
        required=False,
        label='Hora de inicio',
        widget=forms.Select(attrs={'class': 'form-select mb-2', 'id': 'horario_inicio_select'}),
        help_text='Seleccione la hora de inicio de servicios para esta fecha especial'
    )
    
    horario_fin_choices = forms.ChoiceField(
        required=False,
        label='Hora de fin',
        widget=forms.Select(attrs={'class': 'form-select mb-2', 'id': 'horario_fin_select'}),
        help_text='Seleccione la hora de fin de servicios para esta fecha especial'
    )
    
    class Meta:
        model = FechaEspecial
        fields = ['fecha', 'descripcion', 'disponible', 'hora_inicio', 'hora_fin', 'capacidad']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
        help_texts = {
            'fecha': 'Seleccione la fecha especial (festivo, cierre programado, etc.)',
            'descripcion': 'Describa el motivo de esta fecha especial (ej. "Festivo nacional", "Mantenimiento")',
            'disponible': 'Marque esta casilla si el lavadero estará disponible en esta fecha, desmárquela si estará cerrado.',
            'hora_inicio': 'Hora de inicio de servicios para esta fecha especial',
            'hora_fin': 'Hora de fin de servicios para esta fecha especial',
            'capacidad': 'Número máximo de vehículos que pueden ser atendidos simultáneamente en esta fecha',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha'].label = 'Fecha'
        self.fields['descripcion'].label = 'Descripción'
        self.fields['disponible'].label = 'Disponible'
        self.fields['hora_inicio'].label = 'Hora de inicio'
        self.fields['hora_fin'].label = 'Hora de fin'
        self.fields['capacidad'].label = 'Capacidad'
        
        # Inicialmente, los campos de selección de horario están vacíos
        self.fields['horario_inicio_choices'].choices = [('', '-- Seleccione una hora --')]
        self.fields['horario_fin_choices'].choices = [('', '-- Seleccione una hora --')]
        
        # Si hay una fecha seleccionada, cargar los horarios disponibles
        if 'fecha' in self.data and self.data['fecha']:
            try:
                from datetime import datetime
                fecha_seleccionada = datetime.strptime(self.data['fecha'], '%Y-%m-%d').date()
                self.cargar_horarios_disponibles(fecha_seleccionada)
            except (ValueError, TypeError):
                pass
        elif self.instance and self.instance.pk and self.instance.fecha:
            # Si estamos editando un registro existente
            self.cargar_horarios_disponibles(self.instance.fecha)
        
    def cargar_horarios_disponibles(self, fecha):
        """Carga los horarios disponibles según el día de la semana de la fecha seleccionada"""
        # Obtener el día de la semana (0-6, donde 0 es lunes)
        dia_semana = fecha.weekday()
        
        # Buscar disponibilidades para ese día de la semana
        from .models import DisponibilidadHoraria
        from datetime import datetime, timedelta
        
        disponibilidades = DisponibilidadHoraria.objects.filter(
            dia_semana=dia_semana,
            activo=True
        ).order_by('hora_inicio')
        
        # Actualizar las opciones de los campos de selección
        inicio_choices = [('', '-- Seleccione una hora --')]
        fin_choices = [('', '-- Seleccione una hora --')]
        
        # Generar opciones de hora cada 30 minutos para todas las disponibilidades
        all_hours = []
        
        for disp in disponibilidades:
            # Convertir a datetime para poder hacer operaciones
            hora_inicio = datetime.combine(datetime.today().date(), disp.hora_inicio)
            hora_fin = datetime.combine(datetime.today().date(), disp.hora_fin)
            
            # Generar intervalos de 30 minutos
            current_time = hora_inicio
            while current_time < hora_fin:
                time_str = current_time.strftime('%H:%M')
                all_hours.append(time_str)
                current_time += timedelta(minutes=30)
        
        # Eliminar duplicados y ordenar
        all_hours = sorted(set(all_hours))
        
        # Agregar todas las horas disponibles como opciones
        for hour in all_hours:
            inicio_choices.append((hour, hour))
            fin_choices.append((hour, hour))
        
        self.fields['horario_inicio_choices'].choices = inicio_choices
        self.fields['horario_fin_choices'].choices = fin_choices
    
    def clean(self):
        cleaned_data = super().clean()
        disponible = cleaned_data.get('disponible')
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        horario_inicio_choice = cleaned_data.get('horario_inicio_choices')
        horario_fin_choice = cleaned_data.get('horario_fin_choices')
        
        # Si se seleccionó un horario predefinido, usarlo
        if horario_inicio_choice:
            from datetime import datetime
            hora_inicio = datetime.strptime(horario_inicio_choice, '%H:%M').time()
            cleaned_data['hora_inicio'] = hora_inicio
            
        if horario_fin_choice:
            from datetime import datetime
            hora_fin = datetime.strptime(horario_fin_choice, '%H:%M').time()
            cleaned_data['hora_fin'] = hora_fin
        
        if disponible and (not hora_inicio or not hora_fin):
            raise forms.ValidationError("Si el servicio está disponible, debe especificar la hora de inicio y fin.")
            
        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise forms.ValidationError("La hora de inicio debe ser anterior a la hora de fin. Por favor seleccione una hora final mayor que la hora inicial.")
            
        return cleaned_data

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