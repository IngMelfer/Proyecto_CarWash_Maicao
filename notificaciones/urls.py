from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'notificaciones', views.NotificacionViewSet, basename='notificacion')

app_name = 'notificaciones'

urlpatterns = [
    # APIs REST
    path('', include(router.urls)),
    
    # Vistas de notificaciones para clientes
    path('cliente/', views.NotificacionesClienteView.as_view(), name='cliente_notificaciones'),
    
    # Vistas de notificaciones para lavadores
    path('lavador/', views.NotificacionesLavadorView.as_view(), name='lavador_notificaciones'),
    
    # APIs para el sistema de notificaciones
    path('api/contador/', views.contador_notificaciones_api, name='contador_api'),
    path('api/dropdown/', views.notificaciones_dropdown_api, name='dropdown_api'),
    path('api/marcar-leida/<int:notificacion_id>/', views.marcar_notificacion_leida, name='marcar_leida'),
    path('api/marcar-todas-leidas/', views.marcar_todas_leidas, name='marcar_todas_leidas'),
]