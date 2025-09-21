from django.urls import path, include
from . import views

app_name = 'empleados'

urlpatterns = [
    # Vistas para administradores y gerentes
    path('', views.EmpleadoListView.as_view(), name='empleado_list'),
    path('<int:pk>/', views.EmpleadoDetailView.as_view(), name='empleado_detail'),
    path('crear/', views.EmpleadoCreateView.as_view(), name='empleado_create'),
    path('<int:pk>/editar/', views.EmpleadoUpdateView.as_view(), name='empleado_update'),
    path('<int:pk>/eliminar/', views.EmpleadoDeleteView.as_view(), name='empleado_delete'),
    
    # Vistas para empleados
    path('dashboard/', views.dashboard_empleado_view, name='dashboard_empleado'),
    path('<int:empleado_id>/registrar-tiempo/', views.registrar_tiempo_view, name='registrar_tiempo'),
    path('registro-tiempo/', views.registro_tiempo_empleado_view, name='registro_tiempo'),
    path('perfil/', views.perfil_empleado, name='perfil'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
    
    # APIs para AJAX
    path('api/<int:empleado_id>/calificaciones/', views.api_calificaciones_empleado, name='api_calificaciones_empleado'),
    path('api/<int:empleado_id>/tiempo/', views.api_tiempo_empleado, name='api_tiempo_empleado'),
    
    # Cambiar estado de empleado
    path('<int:pk>/toggle-estado/', views.toggle_estado_empleado, name='toggle_estado'),
    
    # Rutas para gestión de cargos
    path('cargos/', views.CargoListView.as_view(), name='cargo_list'),
    path('cargos/crear/', views.CargoCreateView.as_view(), name='cargo_create'),
    path('cargos/<int:pk>/editar/', views.CargoUpdateView.as_view(), name='cargo_update'),
    path('cargos/<int:pk>/eliminar/', views.CargoDeleteView.as_view(), name='cargo_delete'),
    
    # Dashboard de empleados
    path('dashboard/', include('empleados.urls_dashboard')),
]