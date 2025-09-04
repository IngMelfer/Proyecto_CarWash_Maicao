from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Notificacion, ConfiguracionNotificaciones

# Register your models here.

class NotificacionAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para el modelo Notificacion.
    """
    list_display = ('cliente', 'get_tipo_display', 'titulo', 'leida', 'fecha_creacion', 'fecha_lectura')
    list_filter = ('tipo', 'leida', 'fecha_creacion')
    search_fields = ('cliente__nombre', 'cliente__apellido', 'titulo', 'mensaje')
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ('fecha_creacion', 'fecha_lectura')
    
    fieldsets = (
        (_('Información de la Notificación'), {
            'fields': ('cliente', 'tipo', 'titulo', 'mensaje')
        }),
        (_('Estado'), {
            'fields': ('leida', 'fecha_creacion', 'fecha_lectura')
        }),
    )
    
    actions = ['marcar_como_leidas']
    
    def get_tipo_display(self, obj):
        """
        Retorna el tipo de notificación en formato legible.
        """
        return obj.get_tipo_display()
    get_tipo_display.short_description = _('Tipo')
    
    def marcar_como_leidas(self, request, queryset):
        """
        Acción para marcar múltiples notificaciones como leídas.
        """
        for notificacion in queryset:
            notificacion.marcar_como_leida()
        self.message_user(request, _('Las notificaciones seleccionadas han sido marcadas como leídas.'))
    marcar_como_leidas.short_description = _('Marcar como leídas')

class ConfiguracionNotificacionesAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para el modelo ConfiguracionNotificaciones.
    """
    list_display = ('cliente', 'email', 'push', 'sms', 'reservas', 'servicios', 'promociones', 'puntos')
    list_filter = ('email', 'push', 'sms', 'reservas', 'servicios', 'promociones', 'puntos')
    search_fields = ('cliente__nombre', 'cliente__apellido', 'cliente__email')
    
    fieldsets = (
        (_('Cliente'), {
            'fields': ('cliente',)
        }),
        (_('Canales de Notificación'), {
            'fields': ('email', 'push', 'sms')
        }),
        (_('Tipos de Notificación'), {
            'fields': ('reservas', 'servicios', 'promociones', 'puntos')
        }),
    )

admin.site.register(Notificacion, NotificacionAdmin)
admin.site.register(ConfiguracionNotificaciones, ConfiguracionNotificacionesAdmin)
