from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Notificacion
from .serializers import NotificacionSerializer
from clientes.models import Cliente

# Create your views here.

class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para el modelo Notificacion (solo lectura)"""
    serializer_class = NotificacionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titulo', 'mensaje', 'tipo']
    ordering_fields = ['fecha_creacion', 'leida']
    
    def get_queryset(self):
        """Filtrar notificaciones según el usuario"""
        usuario = self.request.user
        
        # Si es admin, no mostrar notificaciones (son personales para clientes)
        if usuario.is_staff:
            return Notificacion.objects.none()
        
        # Si es cliente, mostrar solo sus notificaciones
        try:
            cliente = Cliente.objects.get(usuario=usuario)
            return Notificacion.objects.filter(cliente=cliente).order_by('-fecha_creacion')
        except Cliente.DoesNotExist:
            return Notificacion.objects.none()
    
    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        """Marcar una notificación como leída"""
        notificacion = self.get_object()
        
        # Verificar que el usuario sea el dueño de la notificación
        if request.user != notificacion.cliente.usuario:
            return Response({
                'error': 'No tienes permisos para marcar esta notificación'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Marcar como leída si no lo está
        if not notificacion.leida:
            notificacion.leida = True
            notificacion.fecha_lectura = timezone.now()
            notificacion.save(update_fields=['leida', 'fecha_lectura'])
        
        return Response({
            'mensaje': 'Notificación marcada como leída'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def marcar_todas_leidas(self, request):
        """Marcar todas las notificaciones como leídas"""
        usuario = request.user
        
        try:
            cliente = Cliente.objects.get(usuario=usuario)
            
            # Obtener notificaciones no leídas
            notificaciones = Notificacion.objects.filter(
                cliente=cliente,
                leida=False
            )
            
            # Marcar todas como leídas
            ahora = timezone.now()
            for notificacion in notificaciones:
                notificacion.leida = True
                notificacion.fecha_lectura = ahora
            
            # Actualizar en lote
            Notificacion.objects.bulk_update(
                notificaciones,
                ['leida', 'fecha_lectura']
            )
            
            return Response({
                'mensaje': f'Se han marcado {notificaciones.count()} notificaciones como leídas'
            }, status=status.HTTP_200_OK)
            
        except Cliente.DoesNotExist:
            return Response({
                'error': 'No se encontró el cliente asociado al usuario'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def no_leidas(self, request):
        """Obtener solo notificaciones no leídas"""
        usuario = request.user
        
        try:
            cliente = Cliente.objects.get(usuario=usuario)
            notificaciones = Notificacion.objects.filter(
                cliente=cliente,
                leida=False
            ).order_by('-fecha_creacion')
            
            serializer = self.get_serializer(notificaciones, many=True)
            return Response(serializer.data)
            
        except Cliente.DoesNotExist:
            return Response({
                'error': 'No se encontró el cliente asociado al usuario'
            }, status=status.HTTP_404_NOT_FOUND)
