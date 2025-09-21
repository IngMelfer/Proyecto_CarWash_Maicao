from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Usuario
from .forms import UsuarioAdminForm, UsuarioEditForm

User = get_user_model()

class AdminRequiredMixin:
    """Mixin para verificar que el usuario sea administrador"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('autenticacion:login')
        
        # Verificar si es admin del sistema o admin de autolavado
        if not (request.user.rol in ['admin_sistema', 'admin_autolavado'] or request.user.is_superuser):
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('home')
        
        return super().dispatch(request, *args, **kwargs)


class UsuarioListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    """Vista para listar todos los usuarios del sistema"""
    model = Usuario
    template_name = 'autenticacion/admin/usuario_list.html'
    context_object_name = 'usuarios'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Usuario.objects.all().order_by('-date_joined')
        
        # Filtros de búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Filtro por rol
        rol = self.request.GET.get('rol')
        if rol:
            queryset = queryset.filter(rol=rol)
        
        # Filtro por estado activo
        activo = self.request.GET.get('activo')
        if activo == 'true':
            queryset = queryset.filter(is_active=True)
        elif activo == 'false':
            queryset = queryset.filter(is_active=False)
        
        # Filtro por verificación
        verificado = self.request.GET.get('verificado')
        if verificado == 'true':
            queryset = queryset.filter(is_verified=True)
        elif verificado == 'false':
            queryset = queryset.filter(is_verified=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = Usuario.ROL_CHOICES
        context['search'] = self.request.GET.get('search', '')
        context['rol_selected'] = self.request.GET.get('rol', '')
        context['activo_selected'] = self.request.GET.get('activo', '')
        context['verificado_selected'] = self.request.GET.get('verificado', '')
        return context


class UsuarioCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    """Vista para crear un nuevo usuario"""
    model = Usuario
    form_class = UsuarioAdminForm
    template_name = 'autenticacion/admin/usuario_form.html'
    success_url = reverse_lazy('autenticacion:admin_usuario_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Usuario {form.cleaned_data["email"]} creado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)


class UsuarioUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    """Vista para editar un usuario existente"""
    model = Usuario
    form_class = UsuarioEditForm
    template_name = 'autenticacion/admin/usuario_form.html'
    success_url = reverse_lazy('autenticacion:admin_usuario_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Usuario {form.cleaned_data["email"]} actualizado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores en el formulario.')
        return super().form_invalid(form)


class UsuarioDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    """Vista para eliminar un usuario"""
    model = Usuario
    template_name = 'autenticacion/admin/usuario_confirm_delete.html'
    success_url = reverse_lazy('autenticacion:admin_usuario_list')
    
    def delete(self, request, *args, **kwargs):
        usuario = self.get_object()
        email = usuario.email
        
        # Verificar que no se esté eliminando a sí mismo
        if usuario == request.user:
            messages.error(request, 'No puedes eliminar tu propio usuario.')
            return redirect('autenticacion:admin_usuario_list')
        
        # Verificar que no sea un superusuario (a menos que el usuario actual también lo sea)
        if usuario.is_superuser and not request.user.is_superuser:
            messages.error(request, 'No tienes permisos para eliminar un superusuario.')
            return redirect('autenticacion:admin_usuario_list')
        
        messages.success(request, f'Usuario {email} eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


class UsuarioDetailView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para ver los detalles de un usuario"""
    template_name = 'autenticacion/admin/usuario_detail.html'
    
    def get(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        
        # Obtener información adicional del usuario
        context = {
            'usuario': usuario,
            'tiene_cliente': hasattr(usuario, 'cliente'),
            'tiene_empleado': hasattr(usuario, 'empleado'),
        }
        
        # Si tiene cliente, agregarlo al contexto
        if hasattr(usuario, 'cliente'):
            context['cliente'] = usuario.cliente
        
        # Si tiene empleado, agregarlo al contexto
        if hasattr(usuario, 'empleado'):
            context['empleado'] = usuario.empleado
        
        return render(request, self.template_name, context)


class UsuarioToggleActiveView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para activar/desactivar un usuario"""
    
    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        
        # Verificar que no se esté desactivando a sí mismo
        if usuario == request.user:
            return JsonResponse({
                'success': False,
                'message': 'No puedes desactivar tu propio usuario.'
            })
        
        # Verificar que no sea un superusuario (a menos que el usuario actual también lo sea)
        if usuario.is_superuser and not request.user.is_superuser:
            return JsonResponse({
                'success': False,
                'message': 'No tienes permisos para modificar un superusuario.'
            })
        
        # Cambiar el estado
        usuario.is_active = not usuario.is_active
        usuario.save(update_fields=['is_active'])
        
        estado = 'activado' if usuario.is_active else 'desactivado'
        
        return JsonResponse({
            'success': True,
            'message': f'Usuario {usuario.email} {estado} exitosamente.',
            'is_active': usuario.is_active
        })


class UsuarioToggleVerifiedView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para verificar/desverificar un usuario"""
    
    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        
        # Cambiar el estado de verificación
        usuario.is_verified = not usuario.is_verified
        usuario.save(update_fields=['is_verified'])
        
        estado = 'verificado' if usuario.is_verified else 'desverificado'
        
        return JsonResponse({
            'success': True,
            'message': f'Usuario {usuario.email} {estado} exitosamente.',
            'is_verified': usuario.is_verified
        })


class UsuarioResetPasswordView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para resetear la contraseña de un usuario"""
    
    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        
        # Generar una contraseña temporal
        import secrets
        import string
        
        # Generar contraseña de 8 caracteres
        alphabet = string.ascii_letters + string.digits
        nueva_password = ''.join(secrets.choice(alphabet) for i in range(8))
        
        # Establecer la nueva contraseña
        usuario.set_password(nueva_password)
        usuario.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Contraseña reseteada exitosamente.',
            'nueva_password': nueva_password
        })


# Funciones de vista para AJAX (decoradores)
@login_required
def toggle_usuario_active(request, pk):
    """Función para alternar el estado activo de un usuario"""
    if not (request.user.rol in ['admin_sistema', 'admin_autolavado'] or request.user.is_superuser):
        return JsonResponse({'success': False, 'message': 'Sin permisos'})
    
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=pk)
        usuario.is_active = not usuario.is_active
        usuario.save()
        
        return JsonResponse({
            'success': True,
            'is_active': usuario.is_active,
            'message': f'Usuario {"activado" if usuario.is_active else "desactivado"} exitosamente'
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@login_required
def toggle_usuario_verified(request, pk):
    """Función para alternar el estado de verificación de un usuario"""
    if not (request.user.rol in ['admin_sistema', 'admin_autolavado'] or request.user.is_superuser):
        return JsonResponse({'success': False, 'message': 'Sin permisos'})
    
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=pk)
        usuario.is_verified = not usuario.is_verified
        usuario.save()
        
        return JsonResponse({
            'success': True,
            'is_verified': usuario.is_verified,
            'message': f'Usuario {"verificado" if usuario.is_verified else "no verificado"} exitosamente'
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@login_required
def reset_usuario_password(request, pk):
    """Función para restablecer la contraseña de un usuario"""
    if not (request.user.rol in ['admin_sistema', 'admin_autolavado'] or request.user.is_superuser):
        return JsonResponse({'success': False, 'message': 'Sin permisos'})
    
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, pk=pk)
        
        # Generar nueva contraseña aleatoria
        import string
        import random
        nueva_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        # Establecer nueva contraseña
        usuario.set_password(nueva_password)
        usuario.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Contraseña restablecida exitosamente. Nueva contraseña: {nueva_password}',
            'nueva_password': nueva_password
        })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})