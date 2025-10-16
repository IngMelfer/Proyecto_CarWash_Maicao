from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django import forms
from .models import Servicio, Reserva, DisponibilidadHoraria, Bahia, Vehiculo, HorarioDisponible, MedioPago
from clientes.models import Cliente

# Register your models here.

class BahiaAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para el modelo Bahia.
    """
    list_display = ('nombre', 'descripcion_corta', 'activo', 'tiene_camara', 'mostrar_ip_camara', 'mostrar_qr')
    list_filter = ('activo', 'tiene_camara')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activo', 'tiene_camara')
    
    def descripcion_corta(self, obj):
        """
        Retorna una versión corta de la descripción para mostrar en la lista.
        """
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    
    def mostrar_ip_camara(self, obj):
        """
        Muestra la IP de la cámara si existe.
        """
        return obj.ip_camara if obj.ip_camara else '-'
    
    def mostrar_qr(self, obj):
        """
        Muestra un enlace al código QR si existe.
        """
        if obj.codigo_qr:
            return format_html('<a href="{}" target="_blank">Ver QR</a>', obj.codigo_qr.url)
        return '-'
    
    descripcion_corta.short_description = _('Descripción')
    mostrar_ip_camara.short_description = _('IP Cámara')
    mostrar_qr.short_description = _('Código QR')

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

class ReservaAdminForm(forms.ModelForm):
    """
    Formulario personalizado para el admin de reservas que filtra solo clientes válidos.
    """
    class Meta:
        model = Reserva
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo clientes que tienen un usuario asociado
        self.fields['cliente'].queryset = Cliente.objects.select_related('usuario').filter(usuario__isnull=False)


class ReservaAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para el modelo Reserva.
    """
    form = ReservaAdminForm
    list_display = ('cliente', 'servicio', 'fecha_hora', 'bahia', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_hora', 'fecha_creacion', 'bahia')
    search_fields = ('cliente__nombre', 'cliente__apellido', 'cliente__numero_documento', 'servicio__nombre', 'bahia__nombre')
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

class MedioPagoAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para el modelo MedioPago.
    """
    list_display = ('nombre', 'get_tipo_display', 'descripcion_corta', 'es_pasarela_display', 'activo')
    list_filter = ('tipo', 'activo', 'sandbox')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('activo',)
    
    fieldsets = (
        (_('Información Básica'), {
            'fields': ('nombre', 'tipo', 'descripcion', 'activo')
        }),
        (_('Configuración de Pasarela de Pago'), {
            'fields': ('api_key', 'api_secret', 'merchant_id', 'sandbox'),
            'classes': ('collapse',),
            'description': _('Configure estos campos solo si el medio de pago es una pasarela en línea.')
        }),
    )
    
    def descripcion_corta(self, obj):
        """
        Retorna una versión corta de la descripción para mostrar en la lista.
        """
        return obj.descripcion[:50] + '...' if obj.descripcion and len(obj.descripcion) > 50 else obj.descripcion
    
    def es_pasarela_display(self, obj):
        """
        Muestra si el medio de pago es una pasarela en línea.
        """
        return obj.es_pasarela()
    
    descripcion_corta.short_description = _('Descripción')
    es_pasarela_display.short_description = _('Pasarela')
    es_pasarela_display.boolean = True

class DisponibilidadHorariaAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para el modelo DisponibilidadHoraria.
    """
    list_display = ('dia_semana', 'hora_inicio', 'hora_fin', 'activo')
    list_filter = ('dia_semana', 'activo')
    list_editable = ('hora_inicio', 'hora_fin', 'activo')
    
    actions = ['generar_horarios_disponibles']
    
    def generar_horarios_disponibles(self, request, queryset):
        """
        Acción para generar horarios disponibles a partir de la configuración de disponibilidad horaria.
        """
        from django.core.management import call_command
        call_command('generar_horarios_disponibles')
        self.message_user(request, _('Se han generado los horarios disponibles correctamente.'))
    generar_horarios_disponibles.short_description = _('Generar horarios disponibles')

admin.site.register(Servicio, ServicioAdmin)
admin.site.register(Reserva, ReservaAdmin)
admin.site.register(DisponibilidadHoraria, DisponibilidadHorariaAdmin)
admin.site.register(Bahia, BahiaAdmin)
admin.site.register(Vehiculo)
class HorarioDisponibleAdmin(admin.ModelAdmin):
    """
    Personalización del panel de administración para el modelo HorarioDisponible.
    """
    list_display = ('fecha', 'hora_inicio', 'hora_fin', 'disponible', 'capacidad', 'reservas_actuales')
    list_filter = ('fecha', 'disponible')
    search_fields = ('fecha',)
    date_hierarchy = 'fecha'
    list_editable = ('disponible', 'capacidad')
    
    actions = ['regenerar_horarios_disponibles', 'borrar_todos_horarios_disponibles']
    
    def regenerar_horarios_disponibles(self, request, queryset):
        """
        Acción para regenerar horarios disponibles forzando la actualización.
        """
        from django.core.management import call_command
        call_command('generar_horarios_disponibles', forzar=True)
        self.message_user(request, _('Se han regenerado los horarios disponibles correctamente.'))
    regenerar_horarios_disponibles.short_description = _('Regenerar horarios disponibles')
    
    def borrar_todos_horarios_disponibles(self, request, queryset):
        """
        Acción para borrar todos los horarios disponibles.
        """
        from django.core.management import call_command
        call_command('borrar_horarios_disponibles', confirmar=True)
        self.message_user(request, _('Se han eliminado todos los horarios disponibles correctamente.'))
    borrar_todos_horarios_disponibles.short_description = _('Borrar todos los horarios disponibles')

admin.site.register(HorarioDisponible, HorarioDisponibleAdmin)
admin.site.register(MedioPago, MedioPagoAdmin)
