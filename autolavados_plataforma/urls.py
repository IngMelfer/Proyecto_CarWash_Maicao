"""
URL configuration for autolavados_plataforma project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home_view
from reservas.views_validar import ClienteValidarDirectView

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('autenticacion.urls', namespace='api_autenticacion')),
    path('api/clientes/', include('clientes.urls')),
    path('api/reservas/', include('reservas.urls_api')),
    # Rutas para vistas basadas en plantillas con namespace
    path('notificaciones/', include(('notificaciones.urls', 'notificaciones'), namespace='notificaciones')),
    path('reservas/', include(('reservas.urls', 'reservas'), namespace='reservas')),
    # Ruta directa para validar clientes
    path('clientes/validar/<int:pk>/', ClienteValidarDirectView.as_view(), name='cliente_validar_direct'),
    path('autenticacion/', include(('autenticacion.urls', 'autenticacion'), namespace='autenticacion')),
    path('clientes/', include(('clientes.urls', 'clientes'), namespace='clientes')),
    path('empleados/', include(('empleados.urls', 'empleados'), namespace='empleados')),
    # Namespace específico para el dashboard de empleados
    path('empleados/dashboard/', include(('empleados.urls_dashboard', 'empleados_dashboard'), namespace='empleados_dashboard')),
]

# Servir archivos estáticos y medios en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
