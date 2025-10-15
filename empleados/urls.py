from django.urls import path, include
from . import views

app_name = 'empleados'

urlpatterns = [
    # Vistas para administradores y gerentes
    path('', views.EmpleadoListView.as_view(), name='empleado_list'),
    path('<int:pk>/', views.EmpleadoDetailView.as_view(), name='empleado_detail'),
    path('<int:pk>/editar/', views.EmpleadoUpdateView.as_view(), name='empleado_update'),
    path('<int:pk>/eliminar/', views.EmpleadoDeleteView.as_view(), name='empleado_delete'),
    
    # Vistas para empleados - usando el dashboard específico
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
    
    # Rutas para gestión de tipos de documento
    path('tipos-documento/', views.TipoDocumentoListView.as_view(), name='tipo_documento_list'),
    path('tipos-documento/crear/', views.TipoDocumentoCreateView.as_view(), name='tipo_documento_create'),
    path('tipos-documento/<int:pk>/editar/', views.TipoDocumentoUpdateView.as_view(), name='tipo_documento_update'),
    path('tipos-documento/<int:pk>/eliminar/', views.TipoDocumentoDeleteView.as_view(), name='tipo_documento_delete'),
    
    # Bonificaciones - Empleados
    path('mis-bonificaciones/', views.EmpleadoBonificacionesView.as_view(), name='empleado_bonificaciones'),
    path('cobrar-bonificacion/<int:pk>/', views.EmpleadoCobrarBonificacionView.as_view(), name='empleado_cobrar_bonificacion'),
    
    # Gestión de bonificaciones para administradores
    path('admin-bonificaciones/', views.AdminBonificacionesView.as_view(), name='admin_bonificaciones'),
    path('admin-bonificaciones/crear/', views.BonificacionCreateView.as_view(), name='bonificacion_create'),
    path('admin-bonificaciones/<int:pk>/editar/', views.BonificacionUpdateView.as_view(), name='bonificacion_update'),
    path('admin-bonificaciones/<int:pk>/eliminar/', views.BonificacionDeleteView.as_view(), name='bonificacion_delete'),
    path('admin-bonificaciones/<int:pk>/redimir/', views.RedimirBonificacionView.as_view(), name='redimir_bonificacion'),
    path('admin-bonificaciones/<int:pk>/cobrar/', views.CobrarBonificacionView.as_view(), name='cobrar_bonificacion'),
    path('admin-bonificaciones/evaluar-automaticas/', views.EjecutarEvaluacionAutomaticaView.as_view(), name='evaluar_automaticas'),
    path('admin-bonificaciones/api/empleados/', views.api_empleados_bonificaciones, name='api_empleados_bonificaciones'),
    
    # ===== NUEVAS RUTAS PARA SISTEMA DE BONIFICACIONES V2 =====
    
    # Gestión de configuraciones de bonificaciones (Administradores)
    path('bonificaciones-v2/', views.BonificacionV2ListView.as_view(), name='bonificacion_v2_list'),
    path('bonificaciones-v2/crear/', views.BonificacionV2CreateView.as_view(), name='bonificacion_v2_create'),
    path('bonificaciones-v2/<int:pk>/editar/', views.BonificacionV2UpdateView.as_view(), name='bonificacion_v2_update'),
    path('bonificaciones-v2/<int:pk>/eliminar/', views.BonificacionV2DeleteView.as_view(), name='bonificacion_v2_delete'),
    
    # Gestión de bonificaciones obtenidas (Administradores)
    path('bonificaciones-obtenidas/', views.BonificacionObtenidaListView.as_view(), name='bonificacion_obtenida_list'),
    path('bonificaciones-obtenidas/<int:pk>/redimir/', views.RedimirBonificacionV2View.as_view(), name='redimir_bonificacion_v2'),
    
    # Vista para empleados - sus bonificaciones
    path('mis-bonificaciones-v2/', views.EmpleadoBonificacionesV2View.as_view(), name='empleado_bonificaciones_v2'),
    
    # API para evaluación de bonificaciones
    path('api/evaluar-empleado/<int:empleado_id>/bonificacion/<int:bonificacion_id>/', views.api_evaluar_empleado_bonificacion, name='api_evaluar_empleado_bonificacion'),
    
    # Dashboard de empleados - ruta directa y sistema específico
    path('dashboard-empleado/', views.dashboard_empleado_view, name='dashboard'),
    path('dashboard/', include('empleados.urls_dashboard')),
]