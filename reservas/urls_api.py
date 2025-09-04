from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'servicios', views.ServicioViewSet, basename='servicio')
router.register(r'reservas', views.ReservaViewSet, basename='reserva')

urlpatterns = [
    path('', include(router.urls)),
]