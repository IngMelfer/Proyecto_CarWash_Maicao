from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Empleado, TipoDocumento, Cargo, ConfiguracionBonificacion, Incentivo
from autenticacion.models import Usuario


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
    
    # Campo para indicar si no tiene correo personal
    no_tiene_correo = forms.BooleanField(
        label=_('No tengo correo electrónico personal'),
        required=False,
        initial=False,
        help_text=_('Si se marca, el sistema generará un correo automático para el empleado.'),
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'no_tiene_correo'
        })
    )
    
    class Meta:
        model = Empleado
        fields = [
            'nombre', 'apellido', 'tipo_documento', 'numero_documento',
            'email_personal', 'fecha_nacimiento', 'telefono', 'direccion', 'ciudad',
            'cargo', 'rol', 'disponible', 'fecha_contratacion', 'fotografia'
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
            'email_personal': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
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
            'disponible': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
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
            'email_personal': _('Correo Electrónico'),
            'fecha_nacimiento': _('Fecha de Nacimiento'),
            'telefono': _('Teléfono'),
            'direccion': _('Dirección'),
            'ciudad': _('Ciudad'),
            'cargo': _('Cargo'),
            'rol': _('Rol'),
            'disponible': _('Disponible para Trabajar'),
            'fecha_contratacion': _('Fecha de Contratación'),
            'fotografia': _('Fotografía')
        }
        help_texts = {
            'numero_documento': _('Ingresa el número de documento sin puntos ni espacios.'),
            'email_personal': _('Correo electrónico que se usará para crear la cuenta de usuario.'),
            'telefono': _('Formato: +57 300 123 4567'),
            'fecha_nacimiento': _('Selecciona la fecha de nacimiento del empleado.'),
            'disponible': _('Marca si el empleado está disponible para recibir asignaciones de trabajo.'),
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
        
        # El campo email_personal es requerido solo si no se marca "no_tiene_correo"
        self.fields['email_personal'].required = False
        
        # Los campos de contraseña no son requeridos por defecto
        # La validación se hace en el método clean()
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        
        # Establecer disponible=True por defecto para nuevos empleados
        if not self.instance.pk:  # Solo para nuevos empleados
            self.fields['disponible'].initial = True

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data['numero_documento']
        
        # Verificar que no exista otro empleado con el mismo documento
        if Empleado.objects.filter(numero_documento=numero_documento).exists():
            raise forms.ValidationError(_('Ya existe un empleado con este número de documento.'))
        
        return numero_documento

    def clean(self):
        cleaned_data = super().clean()
        email_personal = cleaned_data.get('email_personal')
        no_tiene_correo = cleaned_data.get('no_tiene_correo', False)
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        generar_password_automatico = cleaned_data.get('generar_password_automatico', True)
        
        # Validar que se proporcione correo o se marque "no tiene correo"
        if not no_tiene_correo and not email_personal:
            raise ValidationError(_('Debe proporcionar un correo electrónico personal o marcar "No tengo correo electrónico personal".'))
        
        # Si tiene correo personal, validar que no exista otro usuario con ese email
        if email_personal and not no_tiene_correo:
            from autenticacion.models import Usuario
            if Usuario.objects.filter(email=email_personal).exists():
                raise ValidationError(_('Ya existe un usuario registrado con este correo electrónico.'))
        
        # Validar contraseñas solo si no se genera automáticamente
        if not generar_password_automatico:
            if not password1:
                raise ValidationError(_('La contraseña es requerida cuando no se genera automáticamente.'))
            if password1 != password2:
                raise ValidationError(_('Las contraseñas no coinciden.'))
            if len(password1) < 8:
                raise ValidationError(_('La contraseña debe tener al menos 8 caracteres.'))
        
        return cleaned_data

    def save(self, commit=True):
        empleado = super().save(commit=False)
        
        if commit:
            from autenticacion.models import Usuario
            from django.db import transaction
            
            # La validación del número de documento ya se hace en clean_numero_documento()
            # No necesitamos duplicar la validación aquí
            
            # USAR TRANSACCIÓN ATÓMICA PARA EVITAR DUPLICADOS
            with transaction.atomic():
                # Verificar si el empleado ya tiene un usuario asignado (solo para empleados existentes)
                if empleado.pk and hasattr(empleado, 'usuario') and empleado.usuario:
                    # El empleado ya existe y tiene usuario, no crear otro
                    return empleado
                
                # Determinar el email a usar con lógica simplificada
                no_tiene_correo = self.cleaned_data.get('no_tiene_correo', False)
                email_personal = self.cleaned_data.get('email_personal')
                numero_documento = self.cleaned_data.get('numero_documento')
                
                if no_tiene_correo or not email_personal or email_personal.strip() == '':
                    # Caso 1: No tiene correo personal o está vacío -> generar automático
                    email = self._generar_email_unico(numero_documento)
                else:
                    # Caso 2: Tiene correo personal -> verificar si está disponible
                    if Usuario.objects.filter(email=email_personal).exists():
                        # El correo personal ya existe, generar uno automático
                        email = self._generar_email_unico(numero_documento)
                    else:
                        # El correo personal está disponible
                        email = email_personal
                
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
                
                # CREAR USUARIO DE FORMA ATÓMICA
                try:
                    # Verificar una vez más antes de crear (dentro de la transacción)
                    if Usuario.objects.filter(email=email).exists():
                        # Si el email ya existe, generar uno nuevo
                        email = self._generar_email_unico(numero_documento)
                    
                    usuario = Usuario.objects.create_user(
                        email=email,
                        password=password,
                        first_name=empleado.nombre,
                        last_name=empleado.apellido,
                        rol=rol_usuario,
                        is_active=True
                    )
                    
                    # Asignar el usuario al empleado y guardar
                    empleado.usuario = usuario
                    empleado.save()
                    
                except Exception as e:
                    # Si algo falla, la transacción se revierte automáticamente
                    raise ValidationError(f'Error al crear el empleado: {str(e)}')
        
        return empleado
    
    def _generar_email_unico(self, numero_documento):
        """Genera un email único basado en el número de documento"""
        base_email = f"empleado_{numero_documento}@autolavado.com"
        email_final = base_email
        contador = 1
        
        # Buscar un email único
        while Usuario.objects.filter(email=email_final).exists():
            email_final = f"empleado_{numero_documento}_{contador}@autolavado.com"
            contador += 1
            
            # Prevenir bucles infinitos
            if contador > 100:
                raise ValidationError('No se pudo generar un email único para el empleado')
        
        return email_final


class EmpleadoEditForm(forms.ModelForm):
    """
    Formulario para que los administradores editen empleados existentes.
    No incluye campos de contraseña.
    """
    
    class Meta:
        model = Empleado
        fields = [
            'nombre', 'apellido', 'tipo_documento', 'numero_documento',
            'fecha_nacimiento', 'telefono', 'direccion', 'ciudad',
            'cargo', 'rol', 'fecha_contratacion', 'activo', 'fotografia'
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
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
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
            'activo': _('Activo'),
            'fotografia': _('Fotografía')
        }
        help_texts = {
            'numero_documento': _('Número de documento sin puntos ni espacios.'),
            'telefono': _('Formato: +57 300 123 4567'),
            'fecha_nacimiento': _('Fecha de nacimiento del empleado.'),
            'fecha_contratacion': _('Fecha en que el empleado inicia labores.'),
            'fotografia': _('Fotografía del empleado (opcional).'),
            'activo': _('Marcar si el empleado está activo en el sistema.')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar solo tipos de documento activos
        self.fields['tipo_documento'].queryset = TipoDocumento.objects.filter(activo=True)
        
        # Filtrar solo cargos activos
        self.fields['cargo'].queryset = Cargo.objects.filter(activo=True)
        
        # Hacer algunos campos opcionales
        self.fields['telefono'].required = False
        self.fields['direccion'].required = False
        self.fields['ciudad'].required = False
        self.fields['fotografia'].required = False

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data['numero_documento']
        
        # Verificar que no exista otro empleado con el mismo documento (excepto el actual)
        if self.instance.pk:
            if Empleado.objects.filter(numero_documento=numero_documento).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError(_('Ya existe un empleado con este número de documento.'))
        else:
            if Empleado.objects.filter(numero_documento=numero_documento).exists():
                raise forms.ValidationError(_('Ya existe un empleado con este número de documento.'))
        
        return numero_documento


class EmpleadoPerfilForm(forms.ModelForm):
    """
    Formulario para que los empleados editen su perfil personal.
    """
    
    class Meta:
        model = Empleado
        fields = [
            'nombre', 'apellido', 'telefono', 'direccion', 'ciudad', 'fotografia'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido'
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
            'fotografia': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'nombre': _('Nombre'),
            'apellido': _('Apellido'),
            'telefono': _('Teléfono'),
            'direccion': _('Dirección'),
            'ciudad': _('Ciudad'),
            'fotografia': _('Fotografía'),
        }


class RegistroTiempoForm(forms.ModelForm):
    """
    Formulario para registrar tiempo de trabajo de empleados.
    """
    
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
        model = Empleado  # Cambiar por el modelo correcto cuando esté disponible
        fields = ['tipo_registro']
        widgets = {
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CambiarPasswordForm(forms.Form):
    """
    Formulario para cambiar contraseña de empleados.
    """
    
    password_actual = forms.CharField(
        label=_('Contraseña Actual'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña actual'
        })
    )
    
    password_nueva = forms.CharField(
        label=_('Nueva Contraseña'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        }),
        help_text=_('La contraseña debe tener al menos 8 caracteres.')
    )
    
    password_confirmacion = forms.CharField(
        label=_('Confirmar Nueva Contraseña'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_password_actual(self):
        password_actual = self.cleaned_data.get('password_actual')
        if password_actual and not self.user.check_password(password_actual):
            raise ValidationError(_('La contraseña actual es incorrecta.'))
        return password_actual
    
    def clean(self):
        cleaned_data = super().clean()
        password_nueva = cleaned_data.get('password_nueva')
        password_confirmacion = cleaned_data.get('password_confirmacion')
        
        if password_nueva and password_confirmacion:
            if password_nueva != password_confirmacion:
                raise ValidationError(_('Las contraseñas no coinciden.'))
        
        return cleaned_data
    
    def save(self):
        """Guarda la nueva contraseña del usuario"""
        password_nueva = self.cleaned_data['password_nueva']
        self.user.set_password(password_nueva)
        self.user.save()


# Formularios para gestión de bonificaciones

class ConfiguracionBonificacionForm(forms.ModelForm):
    """Formulario para crear/editar configuraciones de bonificación"""
    class Meta:
        model = ConfiguracionBonificacion
        fields = [
            'nombre', 'descripcion', 'tipo', 'servicios_requeridos', 
            'calificacion_minima', 'monto_bonificacion', 'activo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'servicios_requeridos': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'calificacion_minima': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5', 'step': '0.1'}),
            'monto_bonificacion': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'tipo': 'Seleccione el tipo de bonificación: por servicios o mensual.',
            'servicios_requeridos': 'Cantidad mínima de servicios para obtener la bonificación.',
            'calificacion_minima': 'Calificación promedio mínima requerida (1-5 estrellas).',
            'monto_bonificacion': 'Monto en pesos que se otorgará como bonificación.',
        }

    def clean_servicios_requeridos(self):
        servicios = self.cleaned_data.get('servicios_requeridos')
        if servicios is not None:
            if servicios <= 0:
                raise ValidationError('El número de servicios requeridos debe ser mayor a cero.')
            if servicios > 1000:  # Límite razonable
                raise ValidationError('El número de servicios requeridos no puede exceder 1000.')
        return servicios

    def clean_calificacion_minima(self):
        calificacion = self.cleaned_data.get('calificacion_minima')
        if calificacion is not None:
            if calificacion < 1 or calificacion > 5:
                raise ValidationError('La calificación mínima debe estar entre 1 y 5.')
        return calificacion

    def clean_monto_bonificacion(self):
        monto = self.cleaned_data.get('monto_bonificacion')
        if monto is not None:
            if monto <= 0:
                raise ValidationError('El monto de bonificación debe ser mayor a cero.')
            if monto > 1000000:  # Límite máximo de 1 millón
                raise ValidationError('El monto de bonificación no puede exceder $1,000,000.')
        return monto


class IncentivoForm(forms.ModelForm):
    """Formulario para crear/editar incentivos manualmente"""
    class Meta:
        model = Incentivo
        fields = [
            'empleado', 'nombre', 'descripcion', 'monto', 'fecha_otorgado',
            'periodo_inicio', 'periodo_fin', 'promedio_calificacion', 'servicios_completados'
        ]
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'fecha_otorgado': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'periodo_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'periodo_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'promedio_calificacion': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5', 'step': '0.01'}),
            'servicios_completados': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar empleados activos
        self.fields['empleado'].queryset = Empleado.objects.filter(activo=True).order_by('nombre', 'apellido')
        
        # Establecer valores por defecto para fechas
        if not self.instance.pk:
            today = timezone.now().date()
            first_day_month = today.replace(day=1)
            self.fields['fecha_otorgado'].initial = today
            self.fields['periodo_inicio'].initial = first_day_month
            self.fields['periodo_fin'].initial = today

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto is not None:
            if monto <= 0:
                raise ValidationError('El monto debe ser mayor a cero.')
            if monto > 1000000:  # Límite máximo de 1 millón
                raise ValidationError('El monto no puede exceder $1,000,000.')
        return monto

    def clean_promedio_calificacion(self):
        calificacion = self.cleaned_data.get('promedio_calificacion')
        if calificacion is not None:
            if calificacion < 1 or calificacion > 5:
                raise ValidationError('La calificación debe estar entre 1 y 5.')
        return calificacion

    def clean_servicios_completados(self):
        servicios = self.cleaned_data.get('servicios_completados')
        if servicios is not None and servicios < 0:
            raise ValidationError('El número de servicios no puede ser negativo.')
        return servicios

    def clean(self):
        cleaned_data = super().clean()
        periodo_inicio = cleaned_data.get('periodo_inicio')
        periodo_fin = cleaned_data.get('periodo_fin')
        fecha_otorgado = cleaned_data.get('fecha_otorgado')

        if periodo_inicio and periodo_fin:
            if periodo_inicio > periodo_fin:
                raise ValidationError('La fecha de inicio del período no puede ser posterior a la fecha de fin.')
        
        if fecha_otorgado and periodo_fin:
            if fecha_otorgado < periodo_fin:
                raise ValidationError('La fecha de otorgamiento no puede ser anterior al fin del período evaluado.')

        # Validar que la fecha de otorgamiento no sea futura
        if fecha_otorgado and fecha_otorgado > timezone.now().date():
            raise ValidationError('La fecha de otorgamiento no puede ser futura.')

        return cleaned_data


class RedimirBonificacionForm(forms.Form):
    """Formulario para redimir una bonificación"""
    motivo_redencion = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label='Motivo de redención',
        help_text='Describa el motivo por el cual se está redimiendo esta bonificación.',
        required=True
    )
    
    confirmar_redencion = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Confirmo que deseo redimir esta bonificación',
        required=True
    )


class FiltrosBonificacionesForm(forms.Form):
    """Formulario para filtrar bonificaciones en la vista de administración"""
    empleado = forms.ModelChoiceField(
        queryset=Empleado.objects.filter(activo=True).order_by('nombre', 'apellido'),
        required=False,
        empty_label="Todos los empleados",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Desde'
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Hasta'
    )
    
    tipo_bonificacion = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + ConfiguracionBonificacion.TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tipo'
    )
    
    monto_minimo = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        label='Monto mínimo'
    )
    
    solo_pendientes = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Solo bonificaciones pendientes de redimir'
    )