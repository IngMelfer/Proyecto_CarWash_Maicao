from django.urls import path
from . import views_dashboard

app_name = 'empleados_dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views_dashboard.dashboard_lavador, name='dashboard'),
    
    # Perfil del empleado
    path('perfil/', views_dashboard.perfil_empleado, name='perfil'),
    path('perfil/editar/', views_dashboard.perfil_empleado, name='editar_perfil'),
    
    # Servicios asignados
    path('servicios/', views_dashboard.servicios_empleado, name='servicios'),
    path('servicios/pendientes/', views_dashboard.servicios_empleado, name='servicios_pendientes'),
    path('servicios/atendidos/', views_dashboard.servicios_empleado, name='servicios_atendidos'),
    path('servicios/cancelados/', views_dashboard.servicios_empleado, name='servicios_cancelados'),
    
    # Calificaciones y reseñas
    path('calificaciones/', views_dashboard.calificaciones_empleado, name='calificaciones'),
    
    # Bonificaciones e incentivos
    path('bonificaciones/', views_dashboard.bonificaciones_empleado, name='bonificaciones'),
    path('bonificaciones/exportar/', views_dashboard.bonificaciones_empleado, name='exportar_bonificaciones'),
    
    # API endpoints para datos dinámicos
    path('api/actualizar-disponibilidad/', views_dashboard.actualizar_disponibilidad, name='api_actualizar_disponibilidad'),
    path('api/estadisticas/', views_dashboard.api_estadisticas, name='api_estadisticas'),
]