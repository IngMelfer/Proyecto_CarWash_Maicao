from django.urls import path
from . import views

urlpatterns = [
    # Rutas para vistas basadas en plantillas
    path('reservar-cita/', views.ReservarCitaView.as_view(), name='reservar_cita'),
    path('mis-citas/', views.MisCitasView.as_view(), name='mis_citas'),
    path('cancelar-cita/<int:cita_id>/', views.CancelarCitaView.as_view(), name='cancelar_cita'),
    path('calificar-cita/<int:cita_id>/', views.CalificarCitaView.as_view(), name='calificar_cita'),
    # Rutas para AJAX
    path('obtener-horarios-disponibles/', views.ObtenerHorariosDisponiblesView.as_view(), name='obtener_horarios_disponibles'),
]