from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Usuario

# Register your models here.

class UsuarioAdmin(UserAdmin):
    """
    Personalización del panel de administración para el modelo Usuario.
    """
    list_display = ('email', 'first_name', 'last_name', 'rol', 'is_staff', 'is_verified')
    list_filter = ('rol', 'is_staff', 'is_superuser', 'is_active', 'is_verified')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Información Personal'), {'fields': ('first_name', 'last_name')}),
        (_('Verificación'), {'fields': ('is_verified',)}),
        (_('Rol de Usuario'), {'fields': ('rol',)}),
        (_('Permisos'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Fechas importantes'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'rol'),
        }),
    )

admin.site.register(Usuario, UsuarioAdmin)
