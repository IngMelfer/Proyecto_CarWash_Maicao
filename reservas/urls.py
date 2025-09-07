from django.urls import path
from . import views

urlpatterns = [
    # Rutas para vistas basadas en plantillas
    path('reservar-turno/', views.ReservarTurnoView.as_view(), name='reservar_turno'),
    path('mis-turnos/', views.MisTurnosView.as_view(), name='mis_turnos'),
    path('cancelar-turno/<int:turno_id>/', views.CancelarTurnoView.as_view(), name='cancelar_turno'),
    path('calificar-turno/<int:turno_id>/', views.CalificarTurnoView.as_view(), name='calificar_turno'),
    path('ver-camara/<str:token>/', views.VerCamaraView.as_view(), name='ver_camara'),
    # Rutas para AJAX
    path('obtener_horarios_disponibles/', views.ObtenerHorariosDisponiblesView.as_view(), name='obtener_horarios_disponibles'),
    path('obtener_bahias_disponibles/', views.ObtenerBahiasDisponiblesView.as_view(), name='obtener_bahias_disponibles'),
    path('obtener_medios_pago/', views.ObtenerMediosPagoView.as_view(), name='obtener_medios_pago'),
    # Rutas para pasarelas de pago
    path('procesar-pago/<int:reserva_id>/', views.ProcesarPagoView.as_view(), name='procesar_pago'),
    path('confirmar-pago/<int:reserva_id>/', views.ConfirmarPagoView.as_view(), name='confirmar_pago'),
    # Callbacks de pasarelas de pago
    path('callback/wompi/', views.WompiCallbackView.as_view(), name='wompi_callback'),
    path('callback/payu/', views.PayUCallbackView.as_view(), name='payu_callback'),
    path('callback/epayco/', views.EpaycoCallbackView.as_view(), name='epayco_callback'),
]