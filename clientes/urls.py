from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'clientes', views.ClienteViewSet, basename='cliente')
router.register(r'historial', views.HistorialServicioViewSet, basename='historial')

urlpatterns = [
    path('', include(router.urls)),
]