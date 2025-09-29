from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from autenticacion.mixins import RolRequiredMixin
from autenticacion.models import Usuario
from reservas.models import Reserva
from .models import Empleado, RegistroTiempo, Calificacion, Incentivo, Cargo, TipoDocumento
from .forms import EmpleadoPerfilForm, RegistroTiempoForm, EmpleadoRegistroForm, CambiarPasswordForm, EmpleadoEditForm

# Create your views here.

class EmpleadoListView(LoginRequiredMixin, RolRequiredMixin, ListView):
    """Vista para listar todos los empleados"""
    model = Empleado
    template_name = 'empleados/empleado_list.html'
    context_object_name = 'empleados'
    roles_permitidos = [Usuario.ROL_ADMIN_SISTEMA, Usuario.ROL_ADMIN_AUTOLAVADO, Usuario.ROL_GERENTE]
    
    def get_queryset(self):
        return Empleado.objects.all().order_by('nombre', 'apellido')


class EmpleadoDetailView(LoginRequiredMixin, RolRequiredMixin, DetailView):
    """Vista para ver el detalle de un empleado"""
    model = Empleado
    template_name = 'empleados/empleado_detail.html'
    context_object_name = 'empleado'
    roles_permitidos = [Usuario.ROL_ADMIN_SISTEMA, Usuario.ROL_ADMIN_AUTOLAVADO, Usuario.ROL_GERENTE]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empleado = self.get_object()
        
        # Obtener calificaciones del empleado
        context['calificaciones'] = empleado.calificaciones.all().order_by('-fecha_calificacion')[:10]
        context['promedio_calificacion'] = empleado.calificaciones.aggregate(promedio=Avg('puntuacion'))['promedio'] or 0
        
        # Obtener registros de tiempo recientes
        context['registros_tiempo'] = empleado.registros_tiempo.all().order_by('-hora_inicio')[:10]
        
        # Obtener incentivos recientes
        context['incentivos'] = empleado.incentivos.all().order_by('-fecha_otorgado')[:5]
        
        return context


class EmpleadoCreateView(LoginRequiredMixin, RolRequiredMixin, CreateView):
    """Vista para crear un nuevo empleado"""
    model = Empleado
    form_class = EmpleadoRegistroForm
    template_name = 'empleados/empleado_form.html'
    success_url = reverse_lazy('empleados:empleado_list')
    roles_permitidos = [Usuario.ROL_ADMIN_SISTEMA, Usuario.ROL_ADMIN_AUTOLAVADO, Usuario.ROL_GERENTE]
    
    def form_valid(self, form):
        empleado = form.save()
        
        # Determinar qué tipo de contraseña se asignó
        generar_automatico = form.cleaned_data.get('generar_password_automatico', True)
        
        if generar_automatico:
            password_info = f'Contraseña inicial: {empleado.numero_documento}'
        else:
            password_info = 'Contraseña personalizada asignada'
        
        # Verificar si el usuario fue creado correctamente
        if hasattr(empleado, 'usuario') and empleado.usuario:
            usuario_info = f'Usuario: {empleado.usuario.email}. '
        else:
            usuario_info = 'Usuario: No se pudo crear el usuario. '
        
        messages.success(
            self.request, 
            f'Empleado {empleado.nombre} {empleado.apellido} creado correctamente. '
            f'{usuario_info}{password_info}'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Recopilar todos los errores del formulario
        errores = []
        
        # Errores de campos específicos
        for field, errors in form.errors.items():
            if field == '__all__':
                errores.extend(errors)
            else:
                field_label = form.fields[field].label or field
                for error in errors:
                    errores.append(f"{field_label}: {error}")
        
        # Mostrar errores específicos
        if errores:
            for error in errores:
                messages.error(self.request, error)
        else:
            messages.error(
                self.request,
                'Error al crear el empleado. Por favor, revisa los datos ingresados.'
            )
        
        return super().form_invalid(form)


class EmpleadoUpdateView(LoginRequiredMixin, RolRequiredMixin, UpdateView):
    """Vista para actualizar un empleado existente"""
    model = Empleado
    form_class = EmpleadoEditForm
    template_name = 'empleados/empleado_form.html'
    success_url = reverse_lazy('empleados:empleado_list')
    roles_permitidos = [Usuario.ROL_ADMIN_SISTEMA, Usuario.ROL_ADMIN_AUTOLAVADO, Usuario.ROL_GERENTE]
    
    def dispatch(self, request, *args, **kwargs):
        # Verificación adicional para asegurar que los administradores de autolavado tengan acceso
        if request.user.rol == Usuario.ROL_ADMIN_AUTOLAVADO:
            return super().dispatch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Guardar el formulario con la foto actualizada
        empleado = form.save(commit=False)
        # Si hay una nueva foto, se procesará automáticamente
        empleado.save()
        
        messages.success(self.request, f'Empleado {form.cleaned_data["nombre"]} {form.cleaned_data["apellido"]} actualizado correctamente')
        return super().form_valid(form)


class EmpleadoDeleteView(LoginRequiredMixin, RolRequiredMixin, DeleteView):
    """Vista para eliminar un empleado"""
    model = Empleado
    template_name = 'empleados/empleado_confirm_delete.html'
    success_url = reverse_lazy('empleados:empleado_list')
    roles_permitidos = [Usuario.ROL_ADMIN_SISTEMA, Usuario.ROL_ADMIN_AUTOLAVADO, Usuario.ROL_GERENTE]
    
    def dispatch(self, request, *args, **kwargs):
        # Verificación adicional para asegurar que los administradores de autolavado tengan acceso
        if request.user.rol == Usuario.ROL_ADMIN_AUTOLAVADO:
            return super().dispatch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        empleado = self.get_object()
        # En lugar de eliminar, marcamos como inactivo
        empleado.activo = False
        empleado.save()
        
        # También actualizamos el usuario asociado
        if empleado.usuario:
            empleado.usuario.is_active = False
            empleado.usuario.save()
            
        messages.success(request, f'Empleado {empleado.nombre} {empleado.apellido} desactivado correctamente')
        return redirect(self.success_url)


@login_required
def registrar_tiempo_view(request, empleado_id):
    """Vista para registrar el tiempo de inicio/fin de un servicio"""
    empleado = get_object_or_404(Empleado, pk=empleado_id)
    
    # Verificar que el usuario sea el empleado o tenga permisos
    if request.user.rol not in [Usuario.ROL_ADMIN_SISTEMA, Usuario.ROL_ADMIN_AUTOLAVADO, Usuario.ROL_GERENTE] and (not hasattr(empleado, 'usuario') or request.user != empleado.usuario):
        messages.error(request, 'No tienes permisos para registrar tiempo para este empleado')
        return redirect('empleados_dashboard:dashboard')
    
    if request.method == 'POST':
        servicio_id = request.POST.get('servicio_id')
        accion = request.POST.get('accion')  # 'inicio' o 'fin'
        
        if accion == 'inicio':
            # Crear nuevo registro de tiempo
            registro = RegistroTiempo.objects.create(
                empleado=empleado,
                servicio_id=servicio_id,
                hora_inicio=timezone.now()
            )
            messages.success(request, 'Tiempo de inicio registrado correctamente')
            
        elif accion == 'fin':
            # Buscar el registro de tiempo abierto para este servicio y empleado
            try:
                registro = RegistroTiempo.objects.get(
                    empleado=empleado,
                    servicio_id=servicio_id,
                    hora_fin__isnull=True
                )
                registro.hora_fin = timezone.now()
                registro.save()  # El cálculo de duración se hace en el método save
                messages.success(request, 'Tiempo de finalización registrado correctamente')
            except RegistroTiempo.DoesNotExist:
                messages.error(request, 'No se encontró un registro de tiempo abierto para este servicio')
    
    # Redirigir a la página de servicios activos o dashboard
    return redirect('empleados_dashboard:dashboard')


@login_required
def registro_tiempo_empleado_view(request):
    """Vista para que los empleados registren su tiempo de trabajo"""
    try:
        empleado = request.user.empleado
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('empleados_dashboard:dashboard')
    
    # Obtener servicios activos del empleado
    servicios_activos = Reserva.objects.filter(
        lavador=empleado,
        estado__in=[Reserva.CONFIRMADA, Reserva.EN_PROCESO]
    ).select_related('servicio', 'cliente', 'vehiculo')
    
    # Obtener registros de tiempo abiertos
    registros_abiertos = RegistroTiempo.objects.filter(
        empleado=empleado,
        hora_fin__isnull=True
    ).select_related('servicio')
    
    if request.method == 'POST':
        servicio_id = request.POST.get('servicio_id')
        accion = request.POST.get('accion')  # 'inicio' o 'fin'
        
        if accion == 'inicio':
            # Crear nuevo registro de tiempo
            registro = RegistroTiempo.objects.create(
                empleado=empleado,
                servicio_id=servicio_id,
                hora_inicio=timezone.now()
            )
            messages.success(request, 'Tiempo de inicio registrado correctamente')
            
        elif accion == 'fin':
            # Buscar el registro de tiempo abierto para este servicio y empleado
            try:
                registro = RegistroTiempo.objects.get(
                    empleado=empleado,
                    servicio_id=servicio_id,
                    hora_fin__isnull=True
                )
                registro.hora_fin = timezone.now()
                registro.save()  # El cálculo de duración se hace en el método save
                messages.success(request, 'Tiempo de finalización registrado correctamente')
            except RegistroTiempo.DoesNotExist:
                messages.error(request, 'No se encontró un registro de tiempo abierto para este servicio')
        
        return redirect('empleados:registro_tiempo')
    
    context = {
        'empleado': empleado,
        'servicios_activos': servicios_activos,
        'registros_abiertos': registros_abiertos,
    }
    
    return render(request, 'empleados/registro_tiempo.html', context)


@login_required
def dashboard_empleado_view(request):
    """Vista del dashboard para empleados"""
    # Verificar que el usuario sea un empleado
    if request.user.rol not in [Usuario.ROL_LAVADOR, Usuario.ROL_GERENTE] and not hasattr(request.user, 'empleado'):
        messages.error(request, 'Esta página es solo para empleados')
        return redirect('home')
    
    try:
        empleado = request.user.empleado
        # Lógica del dashboard
        return render(request, 'empleados/dashboard/dashboard.html', {'empleado': empleado})
    except Empleado.DoesNotExist:
        messages.error(request, 'No se encontró un perfil de empleado asociado a tu usuario')
        return redirect('home')


# Vistas para CRUD de Cargos
class CargoListView(LoginRequiredMixin, RolRequiredMixin, ListView):
    """Vista para listar todos los cargos"""
    model = Cargo
    template_name = 'empleados/cargo_list.html'
    context_object_name = 'cargos'
    roles_permitidos = [Usuario.ROL_ADMIN_SISTEMA, Usuario.ROL_ADMIN_AUTOLAVADO, Usuario.ROL_GERENTE]
    
    def get_queryset(self):
        return Cargo.objects.all().order_by('nombre')


class CargoCreateView(LoginRequiredMixin, RolRequiredMixin, CreateView):
    """Vista para crear un nuevo cargo"""
    model = Cargo
    template_name = 'empleados/cargo_form.html'
    fields = ['codigo', 'nombre', 'descripcion', 'activo']
    success_url = reverse_lazy('empleados:cargo_list')
    roles_permitidos = [Usuario.ROL_ADMIN_SISTEMA, Usuario.ROL_ADMIN_AUTOLAVADO, Usuario.ROL_GERENTE]
    
    def form_valid(self, form):
        messages.success(self.request, f'Cargo {form.cleaned_data["nombre"]} creado correctamente')
        return super().form_valid(form)


class CargoUpdateView(LoginRequiredMixin, RolRequiredMixin, UpdateView):
    """Vista para actualizar un cargo existente"""
    model = Cargo
    template_name = 'empleados/cargo_form.html'
    fields = ['codigo', 'nombre', 'descripcion', 'activo']
    success_url = reverse_lazy('empleados:cargo_list')
    roles_permitidos = [Usuario.ROL_ADMIN_SISTEMA, Usuario.ROL_ADMIN_AUTOLAVADO, Usuario.ROL_GERENTE]
    
    def form_valid(self, form):
        messages.success(self.request, f'Cargo {form.cleaned_data["nombre"]} actualizado correctamente')
        return super().form_valid(form)


class CargoDeleteView(LoginRequiredMixin, RolRequiredMixin, DeleteView):
    """Vista para eliminar un cargo"""
    model = Cargo
    template_name = 'empleados/cargo_confirm_delete.html'
    success_url = reverse_lazy('empleados:cargo_list')
    roles_permitidos = [Usuario.ROL_ADMIN_SISTEMA, Usuario.ROL_ADMIN_AUTOLAVADO, Usuario.ROL_GERENTE]
    
    def delete(self, request, *args, **kwargs):
        cargo = self.get_object()
        nombre = cargo.nombre
        # Verificar si hay empleados usando este cargo
        if cargo.empleados.exists():
            messages.error(request, f'No se puede eliminar el cargo {nombre} porque hay empleados asignados a él')
            return redirect('empleados:cargo_list')
        
        messages.success(request, f'Cargo {nombre} eliminado correctamente')
        return super().delete(request, *args, **kwargs)
    
# Código eliminado - estaba fuera de contexto


# API Views para AJAX

@login_required
def api_calificaciones_empleado(request, empleado_id):
    """API para obtener las calificaciones de un empleado"""
    empleado = get_object_or_404(Empleado, pk=empleado_id)
    
    # Verificar permisos
    if request.user.rol not in [Usuario.ROL_ADMIN_SISTEMA, Usuario.ROL_ADMIN_AUTOLAVADO, Usuario.ROL_GERENTE] and (not hasattr(empleado, 'usuario') or request.user != empleado.usuario):
        return JsonResponse({'error': 'No tienes permisos para ver esta información'}, status=403)
    
    # Obtener calificaciones agrupadas por puntuación
    calificaciones_por_puntuacion = Calificacion.objects.filter(empleado=empleado).values('puntuacion').annotate(total=Count('puntuacion')).order_by('puntuacion')
    
    # Obtener promedio de calificaciones
    promedio = Calificacion.objects.filter(empleado=empleado).aggregate(promedio=Avg('puntuacion'))['promedio'] or 0
    
    # Formatear datos para gráficos
    labels = [f"{c['puntuacion']} estrellas" for c in calificaciones_por_puntuacion]
    data = [c['total'] for c in calificaciones_por_puntuacion]
    
    return JsonResponse({
        'labels': labels,
        'data': data,
        'promedio': round(promedio, 2)
    })


@login_required
def api_tiempo_empleado(request, empleado_id):
    """API para obtener estadísticas de tiempo de un empleado"""
    empleado = get_object_or_404(Empleado, pk=empleado_id)
    
    # Verificar permisos
    if request.user.rol not in [Usuario.ROL_ADMIN_SISTEMA, Usuario.ROL_ADMIN_AUTOLAVADO, Usuario.ROL_GERENTE] and (not hasattr(empleado, 'usuario') or request.user != empleado.usuario):
        return JsonResponse({'error': 'No tienes permisos para ver esta información'}, status=403)
    
    # Obtener registros de tiempo completados (con hora_fin)
    registros = RegistroTiempo.objects.filter(empleado=empleado, hora_fin__isnull=False)
    
    # Calcular tiempo promedio por servicio
    tiempo_promedio = registros.aggregate(promedio=Avg('duracion_minutos'))['promedio'] or 0
    
    # Obtener los últimos 30 días de registros para gráfico de tendencia
    fecha_inicio = timezone.now() - timezone.timedelta(days=30)
    registros_recientes = registros.filter(hora_inicio__gte=fecha_inicio).order_by('hora_inicio')
    
    # Formatear datos para gráficos
    labels = [r.hora_inicio.strftime('%d/%m/%Y') for r in registros_recientes]
    data = [r.duracion_minutos for r in registros_recientes]
    
    return JsonResponse({
        'tiempo_promedio': round(tiempo_promedio, 1),
        'labels': labels,
        'data': data
    })


@login_required
def toggle_estado_empleado(request, pk):
    """Vista para activar/desactivar un empleado"""
    # Verificar roles permitidos
    if request.user.rol not in [Usuario.ROL_ADMIN_SISTEMA, Usuario.ROL_ADMIN_AUTOLAVADO, Usuario.ROL_GERENTE]:
        messages.error(request, 'No tiene permisos para realizar esta acción.')
        return redirect('empleados:empleado_list')
    
    empleado = get_object_or_404(Empleado, pk=pk)
    empleado.activo = not empleado.activo
    empleado.save()
    
    if empleado.activo:
        messages.success(request, f'El empleado {empleado.nombre} {empleado.apellido} ha sido activado.')
    else:
        messages.success(request, f'El empleado {empleado.nombre} {empleado.apellido} ha sido desactivado.')
    
    return redirect('empleados:empleado_list')


@login_required
def cambiar_password(request):
    """Vista para que los empleados cambien su contraseña"""
    # Verificar que el usuario tenga un empleado asociado
    try:
        empleado = request.user.empleado
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('empleados_dashboard:dashboard')
    
    if request.method == 'POST':
        form = CambiarPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
            # Actualizar la sesión para que no se desconecte
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            return redirect('empleados:perfil')
    else:
        form = CambiarPasswordForm(request.user)
    
    return render(request, 'empleados/cambiar_password.html', {
        'form': form,
        'empleado': empleado
    })


@login_required
def perfil_empleado(request):
    """Vista para que los empleados vean y editen su perfil"""
    try:
        empleado = request.user.empleado
    except Empleado.DoesNotExist:
        messages.error(request, 'No tienes un perfil de empleado asociado.')
        return redirect('empleados_dashboard:dashboard')
    
    if request.method == 'POST':
        form = EmpleadoPerfilForm(request.POST, request.FILES, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado correctamente.')
            return redirect('empleados:perfil')
    else:
        form = EmpleadoPerfilForm(instance=empleado)
    
    return render(request, 'empleados/perfil.html', {
        'form': form,
        'empleado': empleado
    })


# ========== VISTAS PARA GESTIÓN DE TIPO DE DOCUMENTO ==========

class TipoDocumentoListView(LoginRequiredMixin, RolRequiredMixin, ListView):
    """Vista para listar todos los tipos de documento"""
    model = TipoDocumento
    template_name = 'empleados/tipo_documento_list.html'
    context_object_name = 'tipos_documento'
    roles_permitidos = [Usuario.ROL_ADMIN_SISTEMA]
    
    def get_queryset(self):
        return TipoDocumento.objects.all().order_by('nombre')


class TipoDocumentoCreateView(LoginRequiredMixin, RolRequiredMixin, CreateView):
    """Vista para crear un nuevo tipo de documento"""
    model = TipoDocumento
    template_name = 'empleados/tipo_documento_form.html'
    fields = ['codigo', 'nombre', 'activo']
    success_url = reverse_lazy('empleados:tipo_documento_list')
    roles_permitidos = [Usuario.ROL_ADMIN_SISTEMA]
    
    def form_valid(self, form):
        messages.success(self.request, 'Tipo de documento creado exitosamente.')
        return super().form_valid(form)


class TipoDocumentoUpdateView(LoginRequiredMixin, RolRequiredMixin, UpdateView):
    """Vista para actualizar un tipo de documento"""
    model = TipoDocumento
    template_name = 'empleados/tipo_documento_form.html'
    fields = ['codigo', 'nombre', 'activo']
    success_url = reverse_lazy('empleados:tipo_documento_list')
    roles_permitidos = [Usuario.ROL_ADMIN_SISTEMA]
    
    def form_valid(self, form):
        messages.success(self.request, 'Tipo de documento actualizado exitosamente.')
        return super().form_valid(form)


class TipoDocumentoDeleteView(LoginRequiredMixin, RolRequiredMixin, DeleteView):
    """Vista para eliminar un tipo de documento"""
    model = TipoDocumento
    template_name = 'empleados/tipo_documento_confirm_delete.html'
    success_url = reverse_lazy('empleados:tipo_documento_list')
    roles_permitidos = [Usuario.ROL_ADMIN_SISTEMA]
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Tipo de documento eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)
