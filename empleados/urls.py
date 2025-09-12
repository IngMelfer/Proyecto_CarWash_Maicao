from django.urls import path
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
    
    # APIs para AJAX
    path('api/<int:empleado_id>/calificaciones/', views.api_calificaciones_empleado, name='api_calificaciones_empleado'),
    path('api/<int:empleado_id>/tiempo/', views.api_tiempo_empleado, name='api_tiempo_empleado'),
    
    # Cambiar estado de empleado
    path('<int:pk>/toggle-estado/', views.toggle_estado_empleado, name='toggle_estado'),
]