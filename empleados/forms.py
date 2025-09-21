from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import Empleado, TipoDocumento, Cargo
from usuarios.models import Usuario


class EmpleadoRegistroForm(forms.ModelForm):
    """
    Formulario para registrar un nuevo empleado.
    """
    
    # Campos adicionales para la contraseña
    password1 = forms.CharField(
        label=_('Contraseña'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa la contraseña'
        }),
        help_text=_('La contraseña debe tener al menos 8 caracteres.')
    )
    
    password2 = forms.CharField(
        label=_('Confirmar Contraseña'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma la contraseña'
        }),
        help_text=_('Ingresa la misma contraseña para verificación.')
    )
    
    # Campo para generar contraseña automáticamente
    generar_password_automatico = forms.BooleanField(
        label=_('Generar contraseña automáticamente'),
        required=False,
        initial=True,
        help_text=_('Si se marca, la contraseña será el número de documento del empleado.'),
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'generar_password_automatico'
        })
    )
    
    class Meta:
        model = Empleado
        fields = [
            'nombre', 'apellido', 'tipo_documento', 'numero_documento',
            'fecha_nacimiento', 'telefono', 'direccion', 'ciudad',
            'cargo', 'rol', 'fecha_contratacion', 'fotografia'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del empleado'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido del empleado'
            }),
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de documento'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+57 300 123 4567'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad de residencia'
            }),
            'cargo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'rol': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_contratacion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fotografia': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'nombre': _('Nombre'),
            'apellido': _('Apellido'),
            'tipo_documento': _('Tipo de Documento'),
            'numero_documento': _('Número de Documento'),
            'fecha_nacimiento': _('Fecha de Nacimiento'),
            'telefono': _('Teléfono'),
            'direccion': _('Dirección'),
            'ciudad': _('Ciudad'),
            'cargo': _('Cargo'),
            'rol': _('Rol'),
            'fecha_contratacion': _('Fecha de Contratación'),
            'fotografia': _('Fotografía')
        }
        help_texts = {
            'numero_documento': _('Ingresa el número de documento sin puntos ni espacios.'),
            'telefono': _('Formato: +57 300 123 4567'),
            'fecha_nacimiento': _('Selecciona la fecha de nacimiento del empleado.'),
            'fecha_contratacion': _('Fecha en que el empleado inicia labores.'),
            'fotografia': _('Sube una fotografía del empleado (opcional).')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar solo tipos de documento activos
        self.fields['tipo_documento'].queryset = TipoDocumento.objects.filter(activo=True)
        
        # Filtrar solo cargos activos
        self.fields['cargo'].queryset = Cargo.objects.filter(activo=True)
        
        # Hacer algunos campos opcionales para el registro inicial
        self.fields['telefono'].required = False
        self.fields['direccion'].required = False
        self.fields['ciudad'].required = False
        self.fields['fotografia'].required = False

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data['numero_documento']
        
        # Verificar que no exista otro empleado con el mismo documento
        if Empleado.objects.filter(numero_documento=numero_documento).exists():
            raise forms.ValidationError(_('Ya existe un empleado con este número de documento.'))
        
        return numero_documento

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        generar_automatico = cleaned_data.get('generar_password_automatico')
        
        # Si no se genera automáticamente, validar las contraseñas
        if not generar_automatico:
            if not password1:
                raise forms.ValidationError(_('Debe ingresar una contraseña o marcar la opción de generar automáticamente.'))
            
            if password1 != password2:
                raise forms.ValidationError(_('Las contraseñas no coinciden.'))
            
            if len(password1) < 8:
                raise forms.ValidationError(_('La contraseña debe tener al menos 8 caracteres.'))
        
        return cleaned_data

    def save(self, commit=True):
        empleado = super().save(commit=False)
        
        if commit:
            # Crear el usuario asociado
            email = f"{empleado.numero_documento}@autolavado.com"
            
            # Verificar que no exista un usuario con este email
            if Usuario.objects.filter(email=email).exists():
                # Si existe, usar un email alternativo
                email = f"empleado_{empleado.numero_documento}@autolavado.com"
            
            # Determinar el rol del usuario basado en el rol del empleado
            if empleado.rol == Empleado.ROL_LAVADOR:
                rol_usuario = Usuario.ROL_LAVADOR
            elif empleado.rol == Empleado.ROL_SUPERVISOR:
                rol_usuario = Usuario.ROL_GERENTE
            else:
                rol_usuario = Usuario.ROL_CLIENTE
            
            # Determinar la contraseña
            generar_automatico = self.cleaned_data.get('generar_password_automatico', True)
            if generar_automatico:
                password = empleado.numero_documento
            else:
                password = self.cleaned_data['password1']
            
            # Crear el usuario
            usuario = Usuario.objects.create_user(
                email=email,
                password=password,
                first_name=empleado.nombre,
                last_name=empleado.apellido,
                rol=rol_usuario,
                is_active=True
            )
            
            empleado.usuario = usuario
            empleado.save()
        
        return empleado