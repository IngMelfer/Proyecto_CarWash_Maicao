from django.urls import path
from . import views, views_admin, views_csrf

urlpatterns = [
    # Rutas para vistas basadas en plantillas
    path('reservar/', views.ReservarTurnoView.as_view(), name='reservar_turno'),
    path('mis-turnos/', views.MisTurnosView.as_view(), name='mis_turnos'),
    path('cancelar-turno/<int:turno_id>/', views.CancelarTurnoView.as_view(), name='cancelar_turno'),
    path('calificar-turno/<int:turno_id>/', views.CalificarTurnoView.as_view(), name='calificar_turno'),
    path('ver-camara/<str:token>/', views.VerCamaraView.as_view(), name='ver_camara'),
    
    # Gestión de vehículos
    path('crear-vehiculo/', views.CrearVehiculoView.as_view(), name='crear_vehiculo'),
    
    # Rutas para AJAX
    path('obtener_horarios_disponibles/', views.ObtenerHorariosDisponiblesView.as_view(), name='obtener_horarios_disponibles'),
    path('obtener_bahias_disponibles/', views.ObtenerBahiasDisponiblesView.as_view(), name='obtener_bahias_disponibles'),
    path('obtener_lavadores_disponibles/', views.ObtenerLavadoresDisponiblesView.as_view(), name='obtener_lavadores_disponibles'),
    path('seleccionar_lavador/<int:reserva_id>/<int:lavador_id>/', views.SeleccionarLavadorView.as_view(), name='seleccionar_lavador'),
    path('obtener_medios_pago/', views.ObtenerMediosPagoView.as_view(), name='obtener_medios_pago'),
    # Rutas para pasarelas de pago
    path('procesar-pago/<int:reserva_id>/', views.ProcesarPagoView.as_view(), name='procesar_pago'),
    path('confirmar-pago/<int:reserva_id>/', views.ConfirmarPagoView.as_view(), name='confirmar_pago'),
    # Callbacks de pasarelas de pago
    path('callback/wompi/', views.WompiCallbackView.as_view(), name='wompi_callback'),
    path('callback/payu/', views.PayUCallbackView.as_view(), name='payu_callback'),
    path('callback/epayco/', views.EpaycoCallbackView.as_view(), name='epayco_callback'),
    
    # Dashboard de administrador
    path('dashboard-admin/', views_admin.DashboardAdminView.as_view(), name='dashboard_admin'),
    path('dashboard-admin/obtener-bahias-info/', views_admin.ObtenerBahiasInfoView.as_view(), name='obtener_bahias_info'),
    
    # CRUD de bahías
    path('bahias/', views_admin.BahiaListView.as_view(), name='bahia_list'),
    path('bahias/crear/', views_admin.BahiaCreateView.as_view(), name='bahia_create'),
    path('bahias/editar/<int:pk>/', views_admin.BahiaUpdateView.as_view(), name='bahia_update'),
    path('bahias/eliminar/<int:pk>/', views_admin.BahiaDeleteView.as_view(), name='bahia_delete'),
    
    # CRUD de servicios
    path('servicios/', views_admin.ServicioListView.as_view(), name='servicio_list'),
    path('servicios/crear/', views_admin.ServicioCreateView.as_view(), name='servicio_create'),
    path('servicios/editar/<int:pk>/', views_admin.ServicioUpdateView.as_view(), name='servicio_update'),
    path('servicios/eliminar/<int:pk>/', views_admin.ServicioDeleteView.as_view(), name='servicio_delete'),
    
    # CRUD de medios de pago
    path('medios-pago/', views_admin.MedioPagoListView.as_view(), name='medio_pago_list'),
    path('medios-pago/crear/', views_admin.MedioPagoCreateView.as_view(), name='medio_pago_create'),
    path('medios-pago/editar/<int:pk>/', views_admin.MedioPagoUpdateView.as_view(), name='medio_pago_update'),
    path('medios-pago/eliminar/<int:pk>/', views_admin.MedioPagoDeleteView.as_view(), name='medio_pago_delete'),
    
    # CRUD de disponibilidad horaria
    path('horarios/', views_admin.DisponibilidadHorariaListView.as_view(), name='disponibilidad_horaria_list'),
    path('horarios/crear/', views_admin.DisponibilidadHorariaCreateView.as_view(), name='disponibilidad_horaria_create'),
    path('horarios/editar/<int:pk>/', views_admin.DisponibilidadHorariaUpdateView.as_view(), name='disponibilidad_horaria_update'),
    path('horarios/eliminar/<int:pk>/', views_admin.DisponibilidadHorariaDeleteView.as_view(), name='disponibilidad_horaria_delete'),
    
    # CRUD de horarios disponibles
    path('horarios-disponibles/', views_admin.HorarioDisponibleListView.as_view(), name='horario_disponible_list'),
    path('horarios-disponibles/crear/', views_admin.HorarioDisponibleCreateView.as_view(), name='horario_disponible_create'),
    path('horarios-disponibles/editar/<int:pk>/', views_admin.HorarioDisponibleUpdateView.as_view(), name='horario_disponible_update'),
    path('horarios-disponibles/eliminar/<int:pk>/', views_admin.HorarioDisponibleDeleteView.as_view(), name='horario_disponible_delete'),
    
    # Se eliminaron las rutas para gestión de fechas especiales
    
    # CRUD de reservas
      path('reservas/', views_admin.ReservaListView.as_view(), name='reserva_list'),
      path('reservas/crear/', views_admin.ReservaCreateView.as_view(), name='reserva_create'),
      path('reservas/editar/<int:pk>/', views_admin.ReservaUpdateView.as_view(), name='reserva_update'),
      path('reservas/eliminar/<int:pk>/', views_admin.ReservaDeleteView.as_view(), name='reserva_delete'),
      path('reservas/detalle/<int:pk>/', views_admin.ReservaDetailView.as_view(), name='reserva_detail'),
      path('reservas/cambiar-estado/<int:pk>/', views_admin.CambiarEstadoReservaView.as_view(), name='cambiar_estado_reserva'),
    
    # CRUD de clientes
      path('clientes/', views_admin.ClienteListView.as_view(), name='cliente_list'),
      path('clientes/crear/', views_admin.ClienteCreateView.as_view(), name='cliente_create'),
      # Se mantiene la ruta de edición para compatibilidad, pero no se mostrará en la interfaz
      path('clientes/editar/<int:pk>/', views_admin.ClienteUpdateView.as_view(), name='cliente_update'),
      path('clientes/eliminar/<int:pk>/', views_admin.ClienteDeleteView.as_view(), name='cliente_delete'),
      path('clientes/validar/<int:pk>/', views_admin.ClienteValidarView.as_view(), name='cliente_validar'),
      path('clientes/detalle/<int:pk>/', views_admin.ClienteDetailView.as_view(), name='cliente_detail'),
      path('clientes/acceso/', views_admin.ClienteAccesoView.as_view(), name='cliente_acceso'),
      # Ruta específica para validar clientes
      path('reservas/clientes/validar/<int:pk>/', views_admin.ClienteValidarAltView.as_view(), name='cliente_validar_alt'),
      
      # Iniciar y finalizar servicio
       path('iniciar-servicio/<int:pk>/', views_admin.IniciarServicioView.as_view(), name='iniciar_servicio'),
       path('finalizar-servicio/<int:pk>/', views_admin.FinalizarServicioView.as_view(), name='finalizar_servicio'),
      
      # Las rutas de bahías ya están definidas arriba
      
      # Rutas para diagnóstico CSRF
      path('csrf-diagnostico/', views_csrf.csrf_diagnostico_view, name='csrf_diagnostico'),
      path('csrf-test/', views_csrf.csrf_test_view, name='csrf_test'),
]