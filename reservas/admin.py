from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Servicio, Reserva, DisponibilidadHoraria

# Register your models here.

class ServicioAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para el modelo Servicio.
    """
    list_display = ('nombre', 'descripcion_corta', 'duracion_minutos', 'precio', 'puntos_otorgados', 'activo')
    list_filter = ('activo', 'duracion_minutos')
    search_fields = ('nombre', 'descripcion_corta', 'descripcion')
    list_editable = ('precio', 'puntos_otorgados', 'activo')
    
    def descripcion_corta(self, obj):
        """
        Retorna una versión corta de la descripción para mostrar en la lista.
        """
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    
    descripcion_corta.short_description = _('Descripción')

class ReservaAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para el modelo Reserva.
    """
    list_display = ('cliente', 'servicio', 'fecha_hora', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_hora', 'fecha_creacion')
    search_fields = ('cliente__nombre', 'cliente__apellido', 'cliente__numero_documento', 'servicio__nombre')
    date_hierarchy = 'fecha_hora'
    readonly_fields = ('fecha_creacion',)
    fieldsets = (
        (_('Información de la Reserva'), {
            'fields': ('cliente', 'servicio', 'fecha_hora')
        }),
        (_('Estado'), {
            'fields': ('estado', 'fecha_creacion')
        }),
        (_('Notas'), {
            'fields': ('notas',)
        }),
    )
    
    actions = ['confirmar_reservas', 'cancelar_reservas']
    
    def confirmar_reservas(self, request, queryset):
        """
        Acción para confirmar múltiples reservas seleccionadas.
        """
        for reserva in queryset:
            reserva.confirmar()
        self.message_user(request, _('Las reservas seleccionadas han sido confirmadas.'))
    confirmar_reservas.short_description = _('Confirmar reservas seleccionadas')
    
    def cancelar_reservas(self, request, queryset):
        """
        Acción para cancelar múltiples reservas seleccionadas.
        """
        for reserva in queryset:
            reserva.cancelar()
        self.message_user(request, _('Las reservas seleccionadas han sido canceladas.'))
    cancelar_reservas.short_description = _('Cancelar reservas seleccionadas')

class DisponibilidadHorariaAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para el modelo DisponibilidadHoraria.
    """
    list_display = ('dia_semana', 'hora_inicio', 'hora_fin', 'activo')
    list_filter = ('dia_semana', 'activo')
    list_editable = ('hora_inicio', 'hora_fin', 'activo')

admin.site.register(Servicio, ServicioAdmin)
admin.site.register(Reserva, ReservaAdmin)
admin.site.register(DisponibilidadHoraria, DisponibilidadHorariaAdmin)
