from rest_framework import permissions

class EsAdministrador(permissions.BasePermission):
    """
    Permiso que solo permite acceso a usuarios con rol de administrador.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'administrador'

class EsEmpleado(permissions.BasePermission):
    """
    Permiso que solo permite acceso a usuarios con rol de empleado.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'empleado'

class EsEmpleadoOAdministrador(permissions.BasePermission):
    """
    Permiso que permite acceso a usuarios con rol de empleado o administrador.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.rol in ['empleado', 'administrador']

class EsEmpleadoPropietario(permissions.BasePermission):
    """
    Permiso que solo permite a un empleado acceder a sus propios datos.
    Los administradores pueden acceder a todos los datos.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Los administradores pueden acceder a todos los datos
        if request.user.rol == 'administrador':
            return True
        
        # Los empleados solo pueden acceder a sus propios datos
        if request.user.rol == 'empleado':
            try:
                # Si el objeto es un empleado
                if hasattr(obj, 'usuario'):
                    return obj.usuario == request.user
                # Si el objeto está relacionado con un empleado
                if hasattr(obj, 'empleado'):
                    return obj.empleado.usuario == request.user
            except AttributeError:
                return False
        
        return False