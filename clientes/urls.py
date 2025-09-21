from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'clientes', views.ClienteViewSet, basename='cliente')
router.register(r'historial', views.HistorialServicioViewSet, basename='historial')

urlpatterns = [
    path('', include(router.urls)),
    path('historial-servicios/', views.HistorialServiciosView.as_view(), name='historial_servicios'),
    path('historial-vehiculo/<int:vehiculo_id>/', views.HistorialVehiculoView.as_view(), name='historial_vehiculo'),
    path('puntos-recompensas/', views.PuntosRecompensasView.as_view(), name='puntos_recompensas'),
    path('dashboard/', views.DashboardClienteView.as_view(), name='dashboard'),
]