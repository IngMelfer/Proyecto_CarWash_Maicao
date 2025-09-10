from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse
from .models import Bahia, Reserva, Servicio, MedioPago, DisponibilidadHoraria
from .forms import BahiaForm, ServicioForm, MedioPagoForm, DisponibilidadHorariaForm, ReservaForm, ClienteForm
from django.utils import timezone
from clientes.models import Cliente

class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin para requerir que el usuario sea administrador"""
    login_url = '/autenticacion/login/'
    
    def test_func(self):
        # Solo permitir acceso a administradores
        return self.request.user.is_staff


class DashboardAdminView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para mostrar el dashboard del administrador con gráfico de bahías"""
    template_name = 'reservas/dashboard_admin.html'
    
    def get(self, request):
        # Obtener todas las bahías
        bahias = Bahia.objects.all()
        
        # Para cada bahía, verificar si está ocupada actualmente
        bahias_info = []
        for bahia in bahias:
            # Buscar reservas activas para esta bahía
            reserva_activa = Reserva.objects.filter(
                bahia=bahia,
                fecha_hora__lte=timezone.now(),
                estado__in=[Reserva.CONFIRMADA, Reserva.EN_PROCESO]
            ).order_by('-fecha_hora').first()
            
            # Determinar el estado de la bahía
            if reserva_activa:
                if reserva_activa.estado == Reserva.EN_PROCESO:
                    estado = 'en_proceso'
                else:
                    estado = 'ocupada'
                # Obtener información del cliente y vehículo
                cliente = reserva_activa.cliente
                vehiculo = reserva_activa.vehiculo
                servicio = reserva_activa.servicio
            else:
                estado = 'disponible'
                cliente = None
                vehiculo = None
                servicio = None
            
            # Agregar información de la bahía al listado
            bahias_info.append({
                'bahia': bahia,
                'estado': estado,
                'cliente': cliente,
                'vehiculo': vehiculo,
                'servicio': servicio,
                'reserva': reserva_activa
            })
        
        # Estadísticas rápidas
        bahias_disponibles = sum(1 for info in bahias_info if info['estado'] == 'disponible')
        bahias_ocupadas = sum(1 for info in bahias_info if info['estado'] == 'ocupada')
        servicios_en_proceso = sum(1 for info in bahias_info if info['estado'] == 'en_proceso')
        
        # Reservas pendientes para hoy
        hoy = timezone.now().date()
        manana = hoy + timezone.timedelta(days=1)
        reservas_pendientes = Reserva.objects.filter(
            fecha_hora__gte=timezone.make_aware(timezone.datetime.combine(hoy, timezone.datetime.min.time())),
            fecha_hora__lt=timezone.make_aware(timezone.datetime.combine(manana, timezone.datetime.min.time())),
            estado=Reserva.PENDIENTE
        ).count()
        
        # Conteos totales para las tarjetas del dashboard
        total_reservas = Reserva.objects.count()
        total_clientes = Cliente.objects.count()
        total_bahias = Bahia.objects.count()
        
        context = {
            'bahias_info': bahias_info,
            'bahias_disponibles': bahias_disponibles,
            'bahias_ocupadas': bahias_ocupadas,
            'servicios_en_proceso': servicios_en_proceso,
            'reservas_pendientes': reservas_pendientes,
            'total_reservas': total_reservas,
            'total_clientes': total_clientes,
            'total_bahias': total_bahias
        }
        
        return render(request, self.template_name, context)


# Vistas CRUD para Gestionar Reservas
class ReservaListView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para listar todas las reservas"""
    template_name = 'reservas/reserva_list.html'
    
    def get(self, request):
        reservas = Reserva.objects.all().order_by('-fecha_hora')
        return render(request, self.template_name, {'reservas': reservas})


class ReservaCreateView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para crear una nueva reserva"""
    template_name = 'reservas/reserva_form.html'
    
    def get(self, request):
        form = ReservaForm()
        return render(request, self.template_name, {
            'form': form, 
            'titulo': 'Crear Nueva Reserva'
        })
    
    def post(self, request):
        form = ReservaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reserva creada exitosamente')
            return redirect('reservas:reserva_list')
        return render(request, self.template_name, {
            'form': form, 
            'titulo': 'Crear Nueva Reserva'
        })


class ReservaUpdateView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para actualizar una reserva existente"""
    template_name = 'reservas/reserva_form.html'
    
    def get(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        form = ReservaForm(instance=reserva)
        return render(request, self.template_name, {
            'form': form, 
            'reserva': reserva,
            'titulo': f'Editar Reserva #{reserva.id}'
        })
    
    def post(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reserva actualizada exitosamente')
            return redirect('reservas:reserva_list')
        return render(request, self.template_name, {
            'form': form, 
            'reserva': reserva,
            'titulo': f'Editar Reserva #{reserva.id}'
        })


class ReservaDeleteView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para eliminar una reserva"""
    template_name = 'reservas/reserva_confirm_delete.html'
    
    def get(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        return render(request, self.template_name, {'reserva': reserva})
    
    def post(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        reserva.delete()
        messages.success(request, f'Reserva #{pk} eliminada exitosamente')
        return redirect('reservas:reserva_list')


class ReservaDetailView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para ver detalles de una reserva"""
    template_name = 'reservas/reserva_detail.html'
    
    def get(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        return render(request, self.template_name, {'reserva': reserva})


class CambiarEstadoReservaView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para cambiar el estado de una reserva"""
    def post(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        nuevo_estado = request.POST.get('estado')
        
        if nuevo_estado in [Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO, Reserva.COMPLETADA, Reserva.CANCELADA]:
            reserva.estado = nuevo_estado
            reserva.save()
            messages.success(request, f'Estado de la reserva actualizado a {reserva.get_estado_display()}')
        else:
            messages.error(request, 'Estado no válido')
            
        return redirect(request.META.get('HTTP_REFERER', reverse('reservas:reserva_list')))


# Vistas CRUD para Gestionar Clientes
class ClienteListView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para listar todos los clientes"""
    template_name = 'reservas/cliente_list.html'
    
    def get(self, request):
        clientes = Cliente.objects.all().order_by('-fecha_registro')
        return render(request, self.template_name, {'clientes': clientes})


class ClienteCreateView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para crear un nuevo cliente"""
    template_name = 'reservas/cliente_form.html'
    
    def get(self, request):
        form = ClienteForm()
        return render(request, self.template_name, {
            'form': form, 
            'titulo': 'Crear Nuevo Cliente'
        })
    
    def post(self, request):
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente creado exitosamente')
            return redirect('reservas:cliente_list')
        return render(request, self.template_name, {
            'form': form, 
            'titulo': 'Crear Nuevo Cliente'
        })


class ClienteUpdateView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para actualizar un cliente existente"""
    template_name = 'reservas/cliente_form.html'
    
    def get(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        form = ClienteForm(instance=cliente)
        return render(request, self.template_name, {
            'form': form, 
            'cliente': cliente,
            'titulo': f'Editar Cliente: {cliente.nombre} {cliente.apellido}'
        })
    
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado exitosamente')
            return redirect('reservas:cliente_list')
        return render(request, self.template_name, {
            'form': form, 
            'cliente': cliente,
            'titulo': f'Editar Cliente: {cliente.nombre} {cliente.apellido}'
        })


class ClienteDeleteView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para eliminar un cliente"""
    template_name = 'reservas/cliente_confirm_delete.html'
    
    def get(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        return render(request, self.template_name, {'cliente': cliente})
    
    def post(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        cliente.delete()
        messages.success(request, f'Cliente {cliente.nombre} {cliente.apellido} eliminado exitosamente')
        return redirect('reservas:cliente_list')


class ClienteDetailView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para ver detalles de un cliente"""
    template_name = 'reservas/cliente_detail.html'
    
    def get(self, request, pk):
        cliente = get_object_or_404(Cliente, pk=pk)
        # Obtener historial de reservas del cliente
        reservas = Reserva.objects.filter(cliente=cliente).order_by('-fecha_hora')
        return render(request, self.template_name, {
            'cliente': cliente,
            'reservas': reservas
        })


# Vistas CRUD para Bahías
class BahiaListView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para listar todas las bahías"""
    template_name = 'reservas/bahia_list.html'
    
    def get(self, request):
        bahias = Bahia.objects.all()
        return render(request, self.template_name, {'bahias': bahias})


# Vistas CRUD para Servicios
class ServicioListView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para listar todos los servicios"""
    template_name = 'reservas/servicio_list.html'
    
    def get(self, request):
        servicios = Servicio.objects.all()
        return render(request, self.template_name, {'servicios': servicios})


class ServicioCreateView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para crear un nuevo servicio"""
    template_name = 'reservas/servicio_form.html'
    
    def get(self, request):
        form = ServicioForm()
        return render(request, self.template_name, {
            'form': form, 
            'titulo': 'Crear Nuevo Servicio'
        })
    
    def post(self, request):
        form = ServicioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio creado exitosamente')
            return redirect('reservas:servicio_list')
        return render(request, self.template_name, {
            'form': form, 
            'titulo': 'Crear Nuevo Servicio'
        })


class ServicioUpdateView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para actualizar un servicio existente"""
    template_name = 'reservas/servicio_form.html'
    
    def get(self, request, pk):
        servicio = get_object_or_404(Servicio, pk=pk)
        form = ServicioForm(instance=servicio)
        return render(request, self.template_name, {
            'form': form, 
            'servicio': servicio,
            'titulo': f'Editar Servicio: {servicio.nombre}'
        })
    
    def post(self, request, pk):
        servicio = get_object_or_404(Servicio, pk=pk)
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio actualizado exitosamente')
            return redirect('reservas:servicio_list')
        return render(request, self.template_name, {
            'form': form, 
            'servicio': servicio,
            'titulo': f'Editar Servicio: {servicio.nombre}'
        })


class ServicioDeleteView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para eliminar un servicio"""
    template_name = 'reservas/servicio_confirm_delete.html'
    
    def get(self, request, pk):
        servicio = get_object_or_404(Servicio, pk=pk)
        return render(request, self.template_name, {'servicio': servicio})
    
    def post(self, request, pk):
        servicio = get_object_or_404(Servicio, pk=pk)
        servicio.delete()
        messages.success(request, f'Servicio {servicio.nombre} eliminado exitosamente')
        return redirect('reservas:servicio_list')


# Vistas CRUD para Medios de Pago
class MedioPagoListView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para listar todos los medios de pago"""
    template_name = 'reservas/medio_pago_list.html'
    
    def get(self, request):
        medios_pago = MedioPago.objects.all()
        return render(request, self.template_name, {'medios_pago': medios_pago})


class MedioPagoCreateView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para crear un nuevo medio de pago"""
    template_name = 'reservas/medio_pago_form.html'
    
    def get(self, request):
        form = MedioPagoForm()
        return render(request, self.template_name, {
            'form': form, 
            'titulo': 'Crear Nuevo Medio de Pago'
        })
    
    def post(self, request):
        form = MedioPagoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medio de pago creado exitosamente')
            return redirect('reservas:medio_pago_list')
        return render(request, self.template_name, {
            'form': form, 
            'titulo': 'Crear Nuevo Medio de Pago'
        })


class MedioPagoUpdateView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para actualizar un medio de pago existente"""
    template_name = 'reservas/medio_pago_form.html'
    
    def get(self, request, pk):
        medio_pago = get_object_or_404(MedioPago, pk=pk)
        form = MedioPagoForm(instance=medio_pago)
        return render(request, self.template_name, {
            'form': form, 
            'medio_pago': medio_pago,
            'titulo': f'Editar Medio de Pago: {medio_pago.nombre}'
        })
    
    def post(self, request, pk):
        medio_pago = get_object_or_404(MedioPago, pk=pk)
        form = MedioPagoForm(request.POST, instance=medio_pago)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medio de pago actualizado exitosamente')
            return redirect('reservas:medio_pago_list')
        return render(request, self.template_name, {
            'form': form, 
            'medio_pago': medio_pago,
            'titulo': f'Editar Medio de Pago: {medio_pago.nombre}'
        })


class MedioPagoDeleteView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para eliminar un medio de pago"""
    template_name = 'reservas/medio_pago_confirm_delete.html'
    
    def get(self, request, pk):
        medio_pago = get_object_or_404(MedioPago, pk=pk)
        return render(request, self.template_name, {'medio_pago': medio_pago})
    
    def post(self, request, pk):
        medio_pago = get_object_or_404(MedioPago, pk=pk)
        medio_pago.delete()
        messages.success(request, f'Medio de pago {medio_pago.nombre} eliminado exitosamente')
        return redirect('reservas:medio_pago_list')


# Vistas CRUD para Disponibilidad Horaria
class DisponibilidadHorariaListView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para listar todas las disponibilidades horarias"""
    template_name = 'reservas/disponibilidad_horaria_list.html'
    
    def get(self, request):
        disponibilidades = DisponibilidadHoraria.objects.all()
        return render(request, self.template_name, {'disponibilidades': disponibilidades})


class DisponibilidadHorariaCreateView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para crear una nueva disponibilidad horaria"""
    template_name = 'reservas/disponibilidad_horaria_form.html'
    
    def get(self, request):
        form = DisponibilidadHorariaForm()
        return render(request, self.template_name, {
            'form': form, 
            'titulo': 'Crear Nueva Disponibilidad Horaria'
        })
    
    def post(self, request):
        form = DisponibilidadHorariaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Disponibilidad horaria creada exitosamente')
            return redirect('reservas:disponibilidad_horaria_list')
        return render(request, self.template_name, {
            'form': form, 
            'titulo': 'Crear Nueva Disponibilidad Horaria'
        })


class DisponibilidadHorariaUpdateView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para actualizar una disponibilidad horaria existente"""
    template_name = 'reservas/disponibilidad_horaria_form.html'
    
    def get(self, request, pk):
        disponibilidad = get_object_or_404(DisponibilidadHoraria, pk=pk)
        form = DisponibilidadHorariaForm(instance=disponibilidad)
        return render(request, self.template_name, {
            'form': form, 
            'disponibilidad': disponibilidad,
            'titulo': f'Editar Disponibilidad Horaria: {disponibilidad.dia_semana} {disponibilidad.hora_inicio}'
        })
    
    def post(self, request, pk):
        disponibilidad = get_object_or_404(DisponibilidadHoraria, pk=pk)
        form = DisponibilidadHorariaForm(request.POST, instance=disponibilidad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Disponibilidad horaria actualizada exitosamente')
            return redirect('reservas:disponibilidad_horaria_list')
        return render(request, self.template_name, {
            'form': form, 
            'disponibilidad': disponibilidad,
            'titulo': f'Editar Disponibilidad Horaria: {disponibilidad.dia_semana} {disponibilidad.hora_inicio}'
        })


class DisponibilidadHorariaDeleteView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para eliminar una disponibilidad horaria"""
    template_name = 'reservas/disponibilidad_horaria_confirm_delete.html'
    
    def get(self, request, pk):
        disponibilidad = get_object_or_404(DisponibilidadHoraria, pk=pk)
        return render(request, self.template_name, {'disponibilidad': disponibilidad})
    
    def post(self, request, pk):
        disponibilidad = get_object_or_404(DisponibilidadHoraria, pk=pk)
        disponibilidad.delete()
        messages.success(request, f'Disponibilidad horaria eliminada exitosamente')
        return redirect('reservas:disponibilidad_horaria_list')


class BahiaCreateView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para crear una nueva bahía"""
    template_name = 'reservas/bahia_form.html'
    
    def get(self, request):
        form = BahiaForm()
        return render(request, self.template_name, {
            'form': form, 
            'titulo': 'Crear Nueva Bahía'
        })
    
    def post(self, request):
        form = BahiaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bahía creada exitosamente')
            return redirect('reservas:bahia_list')
        return render(request, self.template_name, {
            'form': form, 
            'titulo': 'Crear Nueva Bahía'
        })


class BahiaUpdateView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para actualizar una bahía existente"""
    template_name = 'reservas/bahia_form.html'
    
    def get(self, request, pk):
        bahia = get_object_or_404(Bahia, pk=pk)
        form = BahiaForm(instance=bahia)
        return render(request, self.template_name, {
            'form': form, 
            'bahia': bahia,
            'titulo': f'Editar Bahía: {bahia.nombre}'
        })
    
    def post(self, request, pk):
        bahia = get_object_or_404(Bahia, pk=pk)
        form = BahiaForm(request.POST, instance=bahia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bahía actualizada exitosamente')
            return redirect('reservas:bahia_list')
        return render(request, self.template_name, {
            'form': form, 
            'bahia': bahia,
            'titulo': f'Editar Bahía: {bahia.nombre}'
        })


class BahiaDeleteView(LoginRequiredMixin, AdminRequiredMixin, View):
    """Vista para eliminar una bahía"""
    template_name = 'reservas/bahia_confirm_delete.html'
    
    def get(self, request, pk):
        bahia = get_object_or_404(Bahia, pk=pk)
        return render(request, self.template_name, {'bahia': bahia})
    
    def post(self, request, pk):
        bahia = get_object_or_404(Bahia, pk=pk)
        bahia.delete()
        messages.success(request, f'Bahía {bahia.nombre} eliminada exitosamente')
        return redirect('reservas:bahia_list')