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
from .views_csrf import csrf_debug_view, csrf_test_ajax
from .views_admin import (
    UsuarioListView, UsuarioCreateView, UsuarioUpdateView, 
    UsuarioDeleteView, UsuarioDetailView, toggle_usuario_active,
    toggle_usuario_verified, reset_usuario_password
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
    
    # Vistas de diagnóstico CSRF
    path('csrf-debug/', csrf_debug_view, name='csrf_debug'),
    path('csrf-test/', csrf_test_ajax, name='csrf_test'),
    
    # Vistas API
    path('api/registro/', RegistroUsuarioAPIView.as_view(), name='api_registro'),
    path('api/login/', LoginAPIView.as_view(), name='api_login'),
    path('api/logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('api/perfil/', PerfilUsuarioAPIView.as_view(), name='api_perfil'),
    
    # URLs de administración de usuarios
    path('admin/usuarios/', UsuarioListView.as_view(), name='admin_usuario_list'),
    path('admin/usuario/crear/', UsuarioCreateView.as_view(), name='admin_usuario_create'),
    path('admin/usuario/<int:pk>/', UsuarioDetailView.as_view(), name='admin_usuario_detail'),
    path('admin/usuario/<int:pk>/editar/', UsuarioUpdateView.as_view(), name='admin_usuario_update'),
    path('admin/usuario/<int:pk>/eliminar/', UsuarioDeleteView.as_view(), name='admin_usuario_delete'),
    
    # URLs AJAX para acciones rápidas
    path('admin/usuario/<int:pk>/toggle-active/', toggle_usuario_active, name='admin_usuario_toggle_active'),
    path('admin/usuario/<int:pk>/toggle-verified/', toggle_usuario_verified, name='admin_usuario_toggle_verified'),
    path('admin/usuario/<int:pk>/reset-password/', reset_usuario_password, name='admin_usuario_reset_password'),
]