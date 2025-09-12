from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages

from django.shortcuts import render

class RolRequiredMixin(UserPassesTestMixin):
    """
    Mixin para requerir que el usuario tenga un rol específico.
    """
    login_url = '/autenticacion/login/'
    roles_permitidos = []
    mensaje_error = 'No tienes permisos para acceder a esta página.'
    
    def test_func(self):
        # Verificar si el usuario está autenticado y tiene el rol requerido
        if not self.request.user.is_authenticated:
            return False
        return self.request.user.rol in self.roles_permitidos
    
    def handle_no_permission(self):
        messages.error(self.request, self.mensaje_error)
        if not self.request.user.is_authenticated:
            # Usar render en lugar de redirect para romper el ciclo
            return render(self.request, 'autenticacion/login.html', {'direct': '1'})
        return render(self.request, 'autenticacion/acceso_denegado.html')


class AdminSistemaRequiredMixin(RolRequiredMixin):
    """
    Mixin para requerir que el usuario sea Administrador del Sistema.
    """
    roles_permitidos = ['admin_sistema']
    mensaje_error = 'Solo los Administradores del Sistema pueden acceder a esta página.'


class AdminAutolavadoRequiredMixin(RolRequiredMixin):
    """
    Mixin para requerir que el usuario sea Administrador del Autolavado.
    """
    roles_permitidos = ['admin_sistema', 'admin_autolavado']
    mensaje_error = 'Solo los Administradores pueden acceder a esta página.'


class GerenteRequiredMixin(RolRequiredMixin):
    """
    Mixin para requerir que el usuario sea Gerente.
    """
    roles_permitidos = ['admin_sistema', 'admin_autolavado', 'gerente']
    mensaje_error = 'Solo los Gerentes o Administradores pueden acceder a esta página.'


class EmpleadoRequiredMixin(RolRequiredMixin):
    """
    Mixin para requerir que el usuario sea Empleado.
    """
    roles_permitidos = ['admin_sistema', 'admin_autolavado', 'gerente', 'empleado']
    mensaje_error = 'Solo los Empleados, Gerentes o Administradores pueden acceder a esta página.'


class ClienteRequiredMixin(RolRequiredMixin):
    """
    Mixin para requerir que el usuario sea Cliente.
    """
    roles_permitidos = ['cliente']
    mensaje_error = 'Solo los Clientes pueden acceder a esta página.'