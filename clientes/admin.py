from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Cliente, HistorialServicio

# Register your models here.

class HistorialServicioInline(admin.TabularInline):
    """
    Inline para mostrar el historial de servicios de un cliente en el panel de administración.
    """
    model = HistorialServicio
    extra = 0
    readonly_fields = ('fecha_servicio',)

class ClienteAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para el modelo Cliente.
    """
    list_display = ('nombre', 'apellido', 'tipo_documento', 'numero_documento', 'telefono', 'email', 'saldo_puntos')
    list_filter = ('tipo_documento', 'ciudad', 'recibir_notificaciones')
    search_fields = ('nombre', 'apellido', 'numero_documento', 'telefono', 'email')
    inlines = [HistorialServicioInline]
    fieldsets = (
        (_('Información Personal'), {
            'fields': ('nombre', 'apellido', 'tipo_documento', 'numero_documento', 'telefono', 'email')
        }),
        (_('Dirección'), {
            'fields': ('direccion', 'ciudad')
        }),
        (_('Información Adicional'), {
            'fields': ('fecha_nacimiento', 'saldo_puntos', 'recibir_notificaciones')
        }),
    )

class HistorialServicioAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para el modelo HistorialServicio.
    """
    list_display = ('cliente', 'servicio', 'fecha_servicio', 'monto', 'puntos_ganados')
    list_filter = ('servicio', 'fecha_servicio')
    search_fields = ('cliente__nombre', 'cliente__apellido', 'cliente__numero_documento', 'servicio')
    date_hierarchy = 'fecha_servicio'
    readonly_fields = ('fecha_servicio',)
    fieldsets = (
        (_('Cliente y Servicio'), {
            'fields': ('cliente', 'servicio', 'descripcion')
        }),
        (_('Detalles'), {
            'fields': ('fecha_servicio', 'monto', 'puntos_ganados', 'comentarios')
        }),
    )

admin.site.register(Cliente, ClienteAdmin)
admin.site.register(HistorialServicio, HistorialServicioAdmin)
