from django.urls import path
from . import views

urlpatterns = [
    # Rutas para vistas basadas en plantillas
    path('reservar-turno/', views.ReservarTurnoView.as_view(), name='reservar_turno'),
    path('mis-turnos/', views.MisTurnosView.as_view(), name='mis_turnos'),
    path('cancelar-turno/<int:turno_id>/', views.CancelarTurnoView.as_view(), name='cancelar_turno'),
    path('calificar-turno/<int:turno_id>/', views.CalificarTurnoView.as_view(), name='calificar_turno'),
    # Rutas para AJAX
    path('obtener-horarios-disponibles/', views.ObtenerHorariosDisponiblesView.as_view(), name='obtener_horarios_disponibles'),
]