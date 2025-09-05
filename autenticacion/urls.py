from django.urls import path
from django.views.generic import TemplateView
from .views import (
    RegistroUsuarioView,
    RegistroUsuarioAPIView,
    VerificarEmailView,
    LoginView,
    LoginAPIView,
    LogoutView,
    LogoutAPIView,
    PerfilUsuarioView,
    PerfilUsuarioAPIView,
    RecuperarPasswordView,
    ResetPasswordView,
    CambiarPasswordView
)

app_name = 'autenticacion'

urlpatterns = [
    # Vistas de documentación
    path('api/', TemplateView.as_view(template_name='autenticacion/api_docs.html', extra_context={
        'title': 'API de Autenticación',
        'description': 'Endpoints disponibles para autenticación de usuarios',
        'endpoints': [
            {'path': 'api/registro/', 'method': 'POST', 'description': 'Registro de nuevos usuarios'},
            {'path': 'api/verificar-email/<token>/', 'method': 'GET', 'description': 'Verificación de email'},
            {'path': 'api/login/', 'method': 'POST', 'description': 'Inicio de sesión'},
            {'path': 'api/logout/', 'method': 'POST', 'description': 'Cierre de sesión'},
            {'path': 'api/perfil/', 'method': 'GET/PUT', 'description': 'Ver o actualizar perfil de usuario'}
        ]
    }), name='api_docs'),
    
    # Vistas web
    path('registro/', RegistroUsuarioView.as_view(), name='registro'),
    path('verificar-email/<uuid:token>/', VerificarEmailView.as_view(), name='verificar_email'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil'),
    path('cambiar-password/', CambiarPasswordView.as_view(), name='cambiar_password'),
    path('recuperar-password/', RecuperarPasswordView.as_view(), name='recuperar_password'),
    path('reset-password/<uuid:token>/', ResetPasswordView.as_view(), name='reset_password'),
    
    # Vistas API
    path('api/registro/', RegistroUsuarioAPIView.as_view(), name='api_registro'),
    path('api/login/', LoginAPIView.as_view(), name='api_login'),
    path('api/logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('api/perfil/', PerfilUsuarioAPIView.as_view(), name='api_perfil'),
]