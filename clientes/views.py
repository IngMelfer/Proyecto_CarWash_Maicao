from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import models
from datetime import timedelta
from decimal import Decimal
from .models import Cliente, HistorialServicio
from .serializers import ClienteSerializer, HistorialServicioSerializer
from notificaciones.models import Notificacion
from reservas.models import Vehiculo

# Create your views here.

class ClienteViewSet(viewsets.ModelViewSet):
    """ViewSet para el modelo Cliente"""
    serializer_class = ClienteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'apellido', 'email', 'numero_documento']
    ordering_fields = ['nombre', 'apellido', 'fecha_registro']
    
    def get_queryset(self):
        """Filtrar clientes según el tipo de usuario"""
        usuario = self.request.user
        
        # Si es admin, mostrar todos los clientes
        if usuario.is_staff:
            return Cliente.objects.all()
        
        # Si es cliente, mostrar solo su perfil
        try:
            cliente = Cliente.objects.get(usuario=usuario)
            return Cliente.objects.filter(id=cliente.id)
        except Cliente.DoesNotExist:
            return Cliente.objects.none()
    
    def get_permissions(self):
        """Definir permisos según la acción"""
        if self.action in ['destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def historial_servicios(self, request, pk=None):
        """Obtener historial de servicios de un cliente"""
        cliente = self.get_object()
        
        # Verificar que el usuario tenga permisos para ver el historial
        if not request.user.is_staff and request.user != cliente.usuario:
            return Response({
                'error': 'No tienes permisos para ver este historial'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Obtener historial de servicios
        historial = HistorialServicio.objects.filter(cliente=cliente).order_by('-fecha_servicio')
        serializer = HistorialServicioSerializer(historial, many=True)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def redimir_puntos(self, request, pk=None):
        """Redimir puntos de un cliente"""
        cliente = self.get_object()
        
        # Verificar que el usuario tenga permisos para redimir puntos
        if not request.user.is_staff and request.user != cliente.usuario:
            return Response({
                'error': 'No tienes permisos para redimir puntos'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Obtener cantidad de puntos a redimir
        puntos = request.data.get('puntos', 0)
        descripcion = request.data.get('descripcion', 'Redención de puntos')
        
        try:
            puntos = int(puntos)
            if puntos <= 0:
                return Response({
                    'error': 'La cantidad de puntos debe ser mayor a 0'
                }, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({
                'error': 'La cantidad de puntos debe ser un número entero'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que el cliente tenga suficientes puntos
        if cliente.saldo_puntos < puntos:
            return Response({
                'error': f'El cliente no tiene suficientes puntos. Saldo actual: {cliente.saldo_puntos}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Redimir puntos
        cliente.redimir_puntos(puntos)
        
        # Crear notificación
        Notificacion.objects.create(
            cliente=cliente,
            tipo=Notificacion.PUNTOS_REDIMIDOS,
            titulo='Puntos Redimidos',
            mensaje=f'Has redimido {puntos} puntos exitosamente. Tu saldo actual es de {cliente.saldo_puntos} puntos.',
        )
        
        return Response({
            'mensaje': f'Se han redimido {puntos} puntos exitosamente',
            'saldo_actual': cliente.saldo_puntos
        }, status=status.HTTP_200_OK)


class HistorialServicioViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para el modelo HistorialServicio (solo lectura)"""
    serializer_class = HistorialServicioSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['servicio', 'descripcion']
    ordering_fields = ['fecha_servicio', 'monto']
    
    def get_queryset(self):
        """Filtrar historial según el tipo de usuario"""
        usuario = self.request.user
        
        # Si es admin, mostrar todo el historial
        if usuario.is_staff:
            return HistorialServicio.objects.all()
        
        # Si es cliente, mostrar solo su historial
        try:
            cliente = Cliente.objects.get(usuario=usuario)
            return HistorialServicio.objects.filter(cliente=cliente)
        except Cliente.DoesNotExist:
            return HistorialServicio.objects.none()


class HistorialServiciosView(LoginRequiredMixin, View):
    """Vista para mostrar el historial de servicios del cliente"""
    login_url = '/autenticacion/login/'
    
    def get(self, request):
        if not hasattr(request.user, 'cliente'):
            return redirect('home')
        
        # Obtener el historial de servicios del cliente
        historial = HistorialServicio.objects.filter(cliente=request.user.cliente).order_by('-fecha_servicio')
        
        # Añadir información de vehículo a cada servicio del historial
        from reservas.models import Reserva
        for servicio in historial:
            servicio.vehiculo = None
            
            # Buscar la reserva asociada usando múltiples criterios para mayor precisión
            # Primero intentar con fecha exacta
            reserva = Reserva.objects.filter(
                cliente=request.user.cliente,
                fecha_hora=servicio.fecha_servicio,
                servicio__nombre=servicio.servicio
            ).first()
            
            # Si no encuentra con fecha exacta, buscar en un rango de tiempo más amplio
            if not reserva:
                from datetime import timedelta
                fecha_inicio = servicio.fecha_servicio - timedelta(hours=2)
                fecha_fin = servicio.fecha_servicio + timedelta(hours=2)
                
                reserva = Reserva.objects.filter(
                    cliente=request.user.cliente,
                    fecha_hora__range=(fecha_inicio, fecha_fin),
                    servicio__nombre=servicio.servicio,
                    estado=Reserva.COMPLETADA
                ).first()
            
            # Si aún no encuentra, buscar por servicio y fecha del mismo día
            if not reserva:
                from datetime import date
                fecha_servicio = servicio.fecha_servicio.date()
                
                reserva = Reserva.objects.filter(
                    cliente=request.user.cliente,
                    fecha_hora__date=fecha_servicio,
                    servicio__nombre=servicio.servicio,
                    estado=Reserva.COMPLETADA
                ).first()
            
            if reserva and reserva.vehiculo:
                servicio.vehiculo = reserva.vehiculo
        
        return render(request, 'clientes/historial_servicios.html', {
            'historial': historial,
            'cliente': request.user.cliente
        })


class HistorialVehiculoView(LoginRequiredMixin, View):
    """
    Vista para mostrar el historial de servicios de un vehículo específico
    Solo muestra servicios que tienen registro en HistorialServicio (servicios realmente completados)
    """
    login_url = '/autenticacion/login/'
    
    def get(self, request, vehiculo_id):
        try:
            # Verificar que el usuario tenga un cliente asociado
            if not hasattr(request.user, 'cliente'):
                return redirect('home')
            
            # Obtener el vehículo
            vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)
            
            # Verificar que el vehículo pertenezca al cliente actual
            if vehiculo.cliente != request.user.cliente:
                messages.error(request, 'No tienes permiso para ver este vehículo.')
                return redirect('clientes:dashboard')
            
            # Obtener solo los servicios que tienen registro en HistorialServicio
            # Esto garantiza que solo se muestren servicios realmente completados
            historial_servicios_db = HistorialServicio.objects.filter(
                cliente=vehiculo.cliente
            ).select_related('cliente').order_by('-fecha_servicio')
            
            # Filtrar solo los servicios relacionados con este vehículo
            # Para esto, necesitamos verificar que exista una reserva completada para este vehículo
            historial_servicios = []
            total_servicios = 0
            total_gastado = Decimal('0')
            total_puntos = 0
            servicios_count = {}
            
            from reservas.models import Reserva
            for historial in historial_servicios_db:
                # Verificar si existe una reserva completada para este vehículo en la fecha del servicio
                reserva_relacionada = Reserva.objects.filter(
                    vehiculo=vehiculo,
                    cliente=historial.cliente,
                    servicio__nombre=historial.servicio,
                    estado=Reserva.COMPLETADA,
                    fecha_hora__date=historial.fecha_servicio.date()
                ).first()
                
                if reserva_relacionada:
                    # Agregar la reserva al objeto historial para usar en la plantilla
                    historial.reserva = reserva_relacionada
                    historial_servicios.append(historial)
                    total_servicios += 1
                    total_gastado += historial.monto
                    total_puntos += historial.puntos_ganados
                    
                    # Contar servicios para estadísticas
                    servicio_nombre = historial.servicio
                    servicios_count[servicio_nombre] = servicios_count.get(servicio_nombre, 0) + 1
            
            # Determinar el servicio más frecuente
            servicio_mas_frecuente = max(servicios_count.items(), key=lambda x: x[1]) if servicios_count else None
            servicio_frecuente = servicio_mas_frecuente[0] if servicio_mas_frecuente else "Ninguno"
            
            return render(request, 'clientes/historial_vehiculo.html', {
                'vehiculo': vehiculo,
                'historial': historial_servicios,
                'total_servicios': total_servicios,
                'total_gastado': total_gastado,
                'total_puntos': total_puntos,
                'servicio_frecuente': servicio_frecuente,
                'cliente': request.user.cliente
            })
            
        except Exception as e:
            messages.error(request, f'Error al obtener el historial del vehículo: {str(e)}')
            return redirect('clientes:dashboard')


from reservas.models import Recompensa

class PuntosRecompensasView(LoginRequiredMixin, View):
    """Vista para mostrar los puntos y recompensas del cliente y permitir seleccionar una recompensa"""
    login_url = '/autenticacion/login/'
    
    def get(self, request):
        if not hasattr(request.user, 'cliente'):
            return redirect('home')
        
        # Obtener el cliente y su historial de servicios
        cliente = request.user.cliente
        historial = HistorialServicio.objects.filter(cliente=cliente).order_by('-fecha_servicio')
        # Recompensas disponibles (activas)
        recompensas = Recompensa.objects.filter(activo=True).order_by('servicio__nombre', 'puntos_requeridos')
        
        return render(request, 'clientes/puntos_recompensas.html', {
            'cliente': cliente,
            'historial': historial,
            'recompensas': recompensas
        })
    
    def post(self, request):
        if not hasattr(request.user, 'cliente'):
            return redirect('home')
        cliente = request.user.cliente
        recompensa_id = request.POST.get('recompensa_id')
        if not recompensa_id:
            messages.error(request, 'Debe seleccionar una recompensa válida.')
            return redirect('clientes:puntos_recompensas')
        try:
            recompensa = Recompensa.objects.get(id=recompensa_id, activo=True)
        except Recompensa.DoesNotExist:
            messages.error(request, 'La recompensa seleccionada no existe o no está activa.')
            return redirect('clientes:puntos_recompensas')
        
        # Validar puntos del cliente
        if cliente.saldo_puntos < recompensa.puntos_requeridos:
            messages.error(request, 'No tiene puntos suficientes para aplicar esta recompensa.')
            return redirect('clientes:puntos_recompensas')
        
        # Guardar recompensa en sesión
        request.session['recompensa_id'] = recompensa.id
        request.session['recompensa_seleccionada'] = recompensa.nombre
        messages.success(request, f'Recompensa "{recompensa.nombre}" seleccionada. Se aplicará en el próximo pago de una reserva del servicio correspondiente.')
        return redirect('clientes:puntos_recompensas')


class DashboardClienteView(LoginRequiredMixin, View):
    """Vista para mostrar el dashboard personalizado del cliente"""
    login_url = '/autenticacion/login/'
    
    def get(self, request):
        if not hasattr(request.user, 'cliente'):
            return redirect('home')
        
        # Obtener el cliente
        cliente = request.user.cliente
        
        # Obtener estadísticas del cliente
        from reservas.models import Reserva, Vehiculo
        from django.utils import timezone
        
        # Turnos pendientes (solo los que están en el futuro o máximo 2 horas en el pasado)
        ahora = timezone.now()
        limite_pasado = ahora - timedelta(hours=2)  # Dar 2 horas de gracia
        
        turnos_pendientes = Reserva.objects.filter(
            cliente=cliente,
            estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA],
            fecha_hora__gte=limite_pasado  # Solo contar los que no han pasado hace más de 2 horas
        ).count()
        
        # Servicios completados
        historial_servicios = HistorialServicio.objects.filter(cliente=cliente).order_by('-fecha_servicio')
        
        # Añadir información de vehículo a cada servicio del historial
        # Esto es necesario porque el modelo HistorialServicio no tiene un campo vehiculo
        # pero la plantilla dashboard.html intenta acceder a servicio.vehiculo
        for servicio in historial_servicios:
            servicio.vehiculo = None
            # Intentar encontrar la reserva asociada a este servicio por fecha y servicio
            reserva = Reserva.objects.filter(
                cliente=cliente,
                fecha_hora=servicio.fecha_servicio,
                servicio__nombre=servicio.servicio
            ).first()
            if reserva and reserva.vehiculo:
                servicio.vehiculo = reserva.vehiculo
        
        servicios_completados = historial_servicios.count()
        
        # Puntos disponibles
        puntos_disponibles = cliente.saldo_puntos
        
        # Vehículos registrados
        vehiculos_registrados = Vehiculo.objects.filter(cliente=cliente).count()
        
        # Próximos turnos (solo los que están en el futuro o máximo 2 horas en el pasado)
        proximos_turnos = Reserva.objects.filter(
            cliente=cliente,
            estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA],
            fecha_hora__gte=limite_pasado  # Solo mostrar los que no han pasado hace más de 2 horas
        ).order_by('fecha_hora')[:5]
        
        # Vehículos del cliente con contadores específicos
        vehiculos = Vehiculo.objects.filter(cliente=cliente)
        
        # Agregar contadores específicos para cada vehículo
        for vehiculo in vehiculos:
            # Contar servicios completados específicos de este vehículo
            servicios_vehiculo = Reserva.objects.filter(
                vehiculo=vehiculo,
                cliente=cliente,
                estado=Reserva.COMPLETADA
            ).count()
            vehiculo.servicios_completados = servicios_vehiculo
        
        return render(request, 'clientes/dashboard.html', {
            'cliente': cliente,
            'turnos_pendientes': turnos_pendientes,
            'servicios_completados': servicios_completados,
            'puntos_disponibles': puntos_disponibles,
            'vehiculos_registrados': vehiculos_registrados,
            'proximos_turnos': proximos_turnos,
            'vehiculos': vehiculos,
            'historial': historial_servicios[:5]  # Pasar los últimos 5 servicios completados
        })
