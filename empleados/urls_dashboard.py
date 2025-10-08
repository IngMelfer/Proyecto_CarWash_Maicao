from django.urls import path
from . import views_dashboard

app_name = 'empleados_dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views_dashboard.dashboard_lavador, name='dashboard'),
    
    # Perfil del empleado
    path('perfil/', views_dashboard.perfil_empleado, name='perfil'),
    
    # Servicios asignados
    path('servicios/', views_dashboard.servicios_empleado, name='servicios'),
    path('servicios/pendientes/', views_dashboard.servicios_empleado, {'estado_filtro': 'pendientes'}, name='servicios_pendientes'),
    path('servicios/completados/', views_dashboard.servicios_empleado, {'estado_filtro': 'completados'}, name='servicios_completados'),
    path('servicios/cancelados/', views_dashboard.servicios_empleado, {'estado_filtro': 'cancelados'}, name='servicios_cancelados'),
    path('servicios/historial/', views_dashboard.historial_servicios, name='historial_servicios'),

    # Acciones de servicio
    path('servicios/<int:pk>/iniciar/', views_dashboard.iniciar_servicio_reserva, name='iniciar_servicio'),
    path('servicios/<int:pk>/finalizar/', views_dashboard.finalizar_servicio_reserva, name='finalizar_servicio'),
    
    # Calificaciones
    path('calificaciones/', views_dashboard.calificaciones_empleado, name='calificaciones'),
    
    # Incentivos y bonificaciones
    path('incentivos/', views_dashboard.incentivos_empleado, name='incentivos'),
    path('bonificaciones/', views_dashboard.bonificaciones_empleado, name='bonificaciones'),
    path('bonificaciones/exportar/', views_dashboard.exportar_bonificaciones, name='exportar_bonificaciones'),
    
    # APIs
    path('api/disponibilidad/', views_dashboard.actualizar_disponibilidad, name='api_disponibilidad'),
    path('api/estadisticas/', views_dashboard.api_estadisticas, name='api_estadisticas'),
]