from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Cliente, HistorialServicio
from .serializers import ClienteSerializer, HistorialServicioSerializer
from notificaciones.models import Notificacion

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
        
        return render(request, 'clientes/historial_servicios.html', {
            'historial': historial,
            'cliente': request.user.cliente
        })


class PuntosRecompensasView(LoginRequiredMixin, View):
    """Vista para mostrar los puntos y recompensas del cliente"""
    login_url = '/autenticacion/login/'
    
    def get(self, request):
        if not hasattr(request.user, 'cliente'):
            return redirect('home')
        
        # Obtener el cliente y su historial de servicios
        cliente = request.user.cliente
        historial = HistorialServicio.objects.filter(cliente=cliente).order_by('-fecha_servicio')
        
        return render(request, 'clientes/puntos_recompensas.html', {
            'cliente': cliente,
            'historial': historial
        })


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
        
        # Turnos pendientes
        turnos_pendientes = Reserva.objects.filter(
            cliente=cliente,
            estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA]
        ).count()
        
        # Servicios completados
        servicios_completados = HistorialServicio.objects.filter(cliente=cliente).count()
        
        # Puntos disponibles
        puntos_disponibles = cliente.saldo_puntos
        
        # Vehículos registrados
        vehiculos_registrados = Vehiculo.objects.filter(cliente=cliente).count()
        
        # Próximos turnos
        proximos_turnos = Reserva.objects.filter(
            cliente=cliente,
            estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA]
        ).order_by('fecha_hora')[:5]
        
        # Vehículos del cliente
        vehiculos = Vehiculo.objects.filter(cliente=cliente)
        
        return render(request, 'clientes/dashboard.html', {
            'cliente': cliente,
            'turnos_pendientes': turnos_pendientes,
            'servicios_completados': servicios_completados,
            'puntos_disponibles': puntos_disponibles,
            'vehiculos_registrados': vehiculos_registrados,
            'proximos_turnos': proximos_turnos,
            'vehiculos': vehiculos
        })
