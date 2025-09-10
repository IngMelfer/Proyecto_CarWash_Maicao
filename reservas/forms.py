from django import forms
from .models import Bahia, Servicio, MedioPago, DisponibilidadHoraria, Reserva
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