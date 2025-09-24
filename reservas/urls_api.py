from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views_api import verificar_placa_unica

router = DefaultRouter()
router.register(r'servicios', views.ServicioViewSet, basename='servicio')
router.register(r'reservas', views.ReservaViewSet, basename='reserva')
router.register(r'bahias', views.BahiaViewSet, basename='bahia')

urlpatterns = [
    path('', include(router.urls)),
    path('verificar-placa/', verificar_placa_unica, name='verificar_placa_unica'),
]