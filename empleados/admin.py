from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Empleado, RegistroTiempo, Calificacion, Incentivo, TipoDocumento, Cargo
from autenticacion.models import Usuario

# Register your models here.

@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'activo', 'fecha_creacion')
    list_filter = ('activo',)
    search_fields = ('codigo', 'nombre')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    def has_add_permission(self, request):
        # Solo el administrador del sistema puede agregar tipos de documento
        return request.user.is_superuser or (hasattr(request.user, 'rol') and request.user.rol == Usuario.ROL_ADMIN_SISTEMA)
    
    def has_change_permission(self, request, obj=None):
        # Solo el administrador del sistema puede modificar tipos de documento
        return request.user.is_superuser or (hasattr(request.user, 'rol') and request.user.rol == Usuario.ROL_ADMIN_SISTEMA)
    
    def has_delete_permission(self, request, obj=None):
        # Solo el administrador del sistema puede eliminar tipos de documento
        return request.user.is_superuser or (hasattr(request.user, 'rol') and request.user.rol == Usuario.ROL_ADMIN_SISTEMA)
    
    def has_view_permission(self, request, obj=None):
        # Todos los usuarios autenticados pueden ver los tipos de documento
        return request.user.is_authenticated


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'activo', 'fecha_creacion')
    list_filter = ('activo',)
    search_fields = ('codigo', 'nombre', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    def has_add_permission(self, request):
        # Solo el administrador del sistema puede agregar cargos
        return request.user.is_superuser or (hasattr(request.user, 'rol') and request.user.rol == Usuario.ROL_ADMIN_SISTEMA)
    
    def has_change_permission(self, request, obj=None):
        # Solo el administrador del sistema puede modificar cargos
        return request.user.is_superuser or (hasattr(request.user, 'rol') and request.user.rol == Usuario.ROL_ADMIN_SISTEMA)
    
    def has_delete_permission(self, request, obj=None):
        # Solo el administrador del sistema puede eliminar cargos
        return request.user.is_superuser or (hasattr(request.user, 'rol') and request.user.rol == Usuario.ROL_ADMIN_SISTEMA)
    
    def has_view_permission(self, request, obj=None):
        # Todos los usuarios autenticados pueden ver los cargos
        return request.user.is_authenticated

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cargo', 'telefono', 'activo')
    list_filter = ('cargo', 'activo', 'ciudad')
    search_fields = ('nombre', 'apellido', 'numero_documento', 'telefono')
    fieldsets = (
        ('Información Personal', {
            'fields': ('usuario', 'nombre', 'apellido', 'tipo_documento', 'numero_documento', 'fecha_nacimiento')
        }),
        ('Información de Contacto', {
            'fields': ('telefono', 'direccion', 'ciudad')
        }),
        ('Información Laboral', {
            'fields': ('cargo', 'fecha_contratacion', 'activo')
        }),
    )


@admin.register(RegistroTiempo)
class RegistroTiempoAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'servicio', 'hora_inicio', 'hora_fin', 'duracion_minutos')
    list_filter = ('empleado', 'hora_inicio')
    search_fields = ('empleado__nombre', 'empleado__apellido', 'servicio__nombre')
    readonly_fields = ('duracion_minutos',)


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'cliente', 'servicio', 'puntuacion', 'fecha_calificacion')
    list_filter = ('puntuacion', 'fecha_calificacion')
    search_fields = ('empleado__nombre', 'empleado__apellido', 'cliente__nombre', 'cliente__apellido')
    readonly_fields = ('fecha_calificacion',)


@admin.register(Incentivo)
class IncentivoAdmin(admin.ModelAdmin):
    list_display = ('empleado', 'nombre', 'monto', 'fecha_otorgado', 'promedio_calificacion')
    list_filter = ('fecha_otorgado', 'periodo_inicio', 'periodo_fin')
    search_fields = ('empleado__nombre', 'empleado__apellido', 'nombre')
    fieldsets = (
        ('Información del Incentivo', {
            'fields': ('empleado', 'nombre', 'descripcion', 'monto', 'fecha_otorgado')
        }),
        ('Período', {
            'fields': ('periodo_inicio', 'periodo_fin')
        }),
        ('Métricas', {
            'fields': ('promedio_calificacion', 'servicios_completados')
        }),
    )
