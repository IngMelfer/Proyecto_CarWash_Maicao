from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Usuario

User = get_user_model()


class UsuarioAdminForm(forms.ModelForm):
    """Formulario para crear usuarios desde el panel de administración"""
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa la contraseña'
        }),
        help_text='La contraseña debe tener al menos 8 caracteres.'
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma la contraseña'
        }),
        help_text='Ingresa la misma contraseña para verificación.'
    )
    
    class Meta:
        model = Usuario
        fields = [
            'email', 'first_name', 'last_name', 'rol', 
            'is_active', 'is_verified', 'is_staff', 'is_superuser'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido'
            }),
            'rol': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_verified': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_superuser': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'email': 'Correo Electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'rol': 'Rol del Usuario',
            'is_active': 'Usuario Activo',
            'is_verified': 'Email Verificado',
            'is_staff': 'Es Staff',
            'is_superuser': 'Es Superusuario',
        }
        help_texts = {
            'email': 'Dirección de correo electrónico única del usuario.',
            'rol': 'Selecciona el rol que tendrá el usuario en el sistema.',
            'is_active': 'Determina si el usuario puede iniciar sesión.',
            'is_verified': 'Indica si el correo electrónico ha sido verificado.',
            'is_staff': 'Permite acceso al panel de administración de Django.',
            'is_superuser': 'Otorga todos los permisos sin asignarlos explícitamente.',
        }
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden.")
        return password2
    
    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if password1 and len(password1) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return password1
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UsuarioEditForm(forms.ModelForm):
    """Formulario para editar usuarios existentes desde el panel de administración"""
    
    class Meta:
        model = Usuario
        fields = [
            'email', 'first_name', 'last_name', 'rol', 
            'is_active', 'is_verified', 'is_staff', 'is_superuser'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido'
            }),
            'rol': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_verified': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_superuser': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'email': 'Correo Electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'rol': 'Rol del Usuario',
            'is_active': 'Usuario Activo',
            'is_verified': 'Email Verificado',
            'is_staff': 'Es Staff',
            'is_superuser': 'Es Superusuario',
        }
        help_texts = {
            'email': 'Dirección de correo electrónico única del usuario.',
            'rol': 'Selecciona el rol que tendrá el usuario en el sistema.',
            'is_active': 'Determina si el usuario puede iniciar sesión.',
            'is_verified': 'Indica si el correo electrónico ha sido verificado.',
            'is_staff': 'Permite acceso al panel de administración de Django.',
            'is_superuser': 'Otorga todos los permisos sin asignarlos explícitamente.',
        }


class UsuarioPasswordResetForm(forms.Form):
    """Formulario para resetear la contraseña de un usuario"""
    nueva_password = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa la nueva contraseña'
        }),
        help_text='La contraseña debe tener al menos 8 caracteres.'
    )
    confirmar_password = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma la nueva contraseña'
        })
    )
    
    def clean_confirmar_password(self):
        nueva_password = self.cleaned_data.get("nueva_password")
        confirmar_password = self.cleaned_data.get("confirmar_password")
        if nueva_password and confirmar_password and nueva_password != confirmar_password:
            raise ValidationError("Las contraseñas no coinciden.")
        return confirmar_password
    
    def clean_nueva_password(self):
        nueva_password = self.cleaned_data.get("nueva_password")
        if nueva_password and len(nueva_password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return nueva_password