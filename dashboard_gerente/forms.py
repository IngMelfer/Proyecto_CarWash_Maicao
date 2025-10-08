from django import forms
from .models import KPIConfiguracion


class KPIConfiguracionForm(forms.ModelForm):
    class Meta:
        model = KPIConfiguracion
        fields = ['nombre', 'entidad', 'metrica', 'campo', 'estado_filtro', 'periodo_dias', 'umbral_alerta', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'entidad': forms.Select(attrs={'class': 'form-control'}),
            'metrica': forms.Select(attrs={'class': 'form-control'}),
            'campo': forms.Select(attrs={'class': 'form-control', 'data-placeholder': 'Seleccione un campo...'}),
            'estado_filtro': forms.TextInput(attrs={'class': 'form-control'}),
            'periodo_dias': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'umbral_alerta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }