from django import forms
from .models import Empleado, RegistroTiempo, Calificacion, Incentivo, TipoDocumento, Cargo
from autenticacion.models import Usuario

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre', 'apellido', 'tipo_documento', 'numero_documento', 
                 'email_personal', 'telefono', 'direccion', 'ciudad', 'fecha_nacimiento', 'cargo', 
                 'fecha_contratacion', 'fotografia', 'activo']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_contratacion': forms.DateInput(attrs={'type': 'date'}),
            'fotografia': forms.FileInput(attrs={'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            if field_name != 'activo':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-check-input'
                
        # Asegurarse de que el campo de fotografía no tenga la clase form-control
        if 'fotografia' in self.fields:
            self.fields['fotografia'].widget.attrs.pop('class', None)

class RegistroTiempoForm(forms.ModelForm):
    TIPO_REGISTRO_CHOICES = [
        ('inicio_servicio', 'Inicio de Servicio'),
        ('fin_servicio', 'Fin de Servicio'),
        ('inicio_descanso', 'Inicio de Descanso'),
        ('fin_descanso', 'Fin de Descanso'),
    ]
    
    tipo_registro = forms.ChoiceField(
        choices=TIPO_REGISTRO_CHOICES,
        label="Tipo de Registro",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = RegistroTiempo
        fields = ['tipo_registro', 'servicio', 'notas']
        widgets = {
            'servicio': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.empleado = kwargs.pop('empleado', None)
        self.estado_actual = kwargs.pop('estado_actual', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar opciones de tipo_registro según el estado actual
        if self.estado_actual == 'trabajando':
            self.fields['tipo_registro'].choices = [
                ('fin_servicio', 'Fin de Servicio'),
                ('inicio_descanso', 'Inicio de Descanso'),
            ]
        elif self.estado_actual == 'descanso':
            self.fields['tipo_registro'].choices = [
                ('fin_descanso', 'Fin de Descanso'),
            ]
        else:  # No ha iniciado actividad
            self.fields['tipo_registro'].choices = [
                ('inicio_servicio', 'Inicio de Servicio'),
            ]
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_registro = cleaned_data.get('tipo_registro')
        servicio = cleaned_data.get('servicio')
        
        # Validar que se seleccione un servicio cuando es inicio de servicio
        if tipo_registro == 'inicio_servicio' and not servicio:
            self.add_error('servicio', 'Debe seleccionar un servicio para iniciar.')
        
        return cleaned_data

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['puntuacion', 'comentario']
        widgets = {
            'puntuacion': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class IncentivoForm(forms.ModelForm):
    class Meta:
        model = Incentivo
        fields = ['empleado', 'nombre', 'monto', 'descripcion', 'fecha_otorgado', 'periodo_inicio', 'periodo_fin']
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_otorgado': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'periodo_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'periodo_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }