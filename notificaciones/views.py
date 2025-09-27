from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Notificacion
from .serializers import NotificacionSerializer
from clientes.models import Cliente
from empleados.models import Empleado

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
    
    @action(detail=False, methods=['post'])
    def marcar_todas_leidas(self, request):
        """Marcar todas las notificaciones del cliente como leídas"""
        try:
            cliente = request.user.cliente
            notificaciones_no_leidas = Notificacion.objects.filter(
                cliente=cliente,
                leida=False
            )
            
            count = notificaciones_no_leidas.count()
            notificaciones_no_leidas.update(
                leida=True,
                fecha_lectura=timezone.now()
            )
            
            return Response({
                'success': True,
                'message': f'{count} notificaciones marcadas como leídas',
                'count': count
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=400)
    
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


# Vistas adicionales para el sistema de notificaciones

class NotificacionesClienteView(LoginRequiredMixin, ListView):
    """Vista para mostrar las notificaciones del cliente"""
    model = Notificacion
    template_name = 'notificaciones/cliente.html'
    context_object_name = 'notificaciones'
    paginate_by = 20
    login_url = '/autenticacion/login/'

    def get_queryset(self):
        if hasattr(self.request.user, 'cliente'):
            return Notificacion.objects.filter(
                cliente=self.request.user.cliente
            ).order_by('-fecha_creacion')
        return Notificacion.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'cliente'):
            notificaciones_no_leidas = Notificacion.objects.filter(
                cliente=self.request.user.cliente,
                leida=False
            ).count()
            total_notificaciones = Notificacion.objects.filter(
                cliente=self.request.user.cliente
            ).count()
            
            context.update({
                'notificaciones_no_leidas': notificaciones_no_leidas,
                'total_notificaciones': total_notificaciones,
            })
        return context


class NotificacionesLavadorView(LoginRequiredMixin, ListView):
    """Vista para mostrar las notificaciones del lavador"""
    model = Notificacion
    template_name = 'notificaciones/lavador.html'
    context_object_name = 'notificaciones'
    paginate_by = 20
    login_url = '/autenticacion/login/'

    def get_queryset(self):
        if hasattr(self.request.user, 'empleado'):
            # Mostrar notificaciones específicas para el empleado
            return Notificacion.objects.filter(
                empleado=self.request.user.empleado,
                tipo__in=[Notificacion.CALIFICACION_RECIBIDA, Notificacion.SERVICIO_ASIGNADO]
            ).order_by('-fecha_creacion')
        return Notificacion.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'empleado'):
            notificaciones_no_leidas = Notificacion.objects.filter(
                empleado=self.request.user.empleado,
                tipo__in=[Notificacion.CALIFICACION_RECIBIDA, Notificacion.SERVICIO_ASIGNADO],
                leida=False
            ).count()
            total_notificaciones = Notificacion.objects.filter(
                empleado=self.request.user.empleado,
                tipo__in=[Notificacion.CALIFICACION_RECIBIDA, Notificacion.SERVICIO_ASIGNADO]
            ).count()
            calificaciones_recibidas = Notificacion.objects.filter(
                empleado=self.request.user.empleado,
                tipo=Notificacion.CALIFICACION_RECIBIDA
            ).count()
            servicios_asignados = Notificacion.objects.filter(
                empleado=self.request.user.empleado,
                tipo=Notificacion.SERVICIO_ASIGNADO
            ).count()
            
            context.update({
                'notificaciones_no_leidas': notificaciones_no_leidas,
                'total_notificaciones': total_notificaciones,
                'calificaciones_recibidas': calificaciones_recibidas,
                'servicios_asignados': servicios_asignados,
            })
        return context


@login_required
@require_http_methods(["GET"])
def contador_notificaciones_api(request):
    """API para obtener el contador de notificaciones no leídas"""
    count = 0
    
    if hasattr(request.user, 'cliente'):
        count = Notificacion.objects.filter(
            cliente=request.user.cliente,
            leida=False
        ).count()
    elif hasattr(request.user, 'empleado'):
        count = Notificacion.objects.filter(
            empleado=request.user.empleado,
            tipo__in=[Notificacion.CALIFICACION_RECIBIDA, Notificacion.SERVICIO_ASIGNADO],
            leida=False
        ).count()
    
    return JsonResponse({'count': count})


@login_required
@require_http_methods(["POST"])
def marcar_todas_leidas(request):
    """Marcar todas las notificaciones como leídas"""
    try:
        if hasattr(request.user, 'cliente'):
            notificaciones = Notificacion.objects.filter(
                cliente=request.user.cliente,
                leida=False
            )
        elif hasattr(request.user, 'empleado'):
            notificaciones = Notificacion.objects.filter(
                empleado=request.user.empleado,
                tipo__in=[Notificacion.CALIFICACION_RECIBIDA, Notificacion.SERVICIO_ASIGNADO],
                leida=False
            )
        else:
            return JsonResponse({'success': False, 'error': 'Usuario no válido'})
        
        count = notificaciones.count()
        notificaciones.update(
            leida=True,
            fecha_lectura=timezone.now()
        )
        
        return JsonResponse({
            'success': True, 
            'message': f'{count} notificaciones marcadas como leídas'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def marcar_notificacion_leida(request, notificacion_id):
    """Marcar una notificación como leída"""
    try:
        if hasattr(request.user, 'cliente'):
            notificacion = get_object_or_404(
                Notificacion, 
                id=notificacion_id, 
                cliente=request.user.cliente
            )
        elif hasattr(request.user, 'empleado'):
            notificacion = get_object_or_404(
                Notificacion, 
                id=notificacion_id, 
                empleado=request.user.empleado,
                tipo__in=[Notificacion.CALIFICACION_RECIBIDA, Notificacion.SERVICIO_ASIGNADO]
            )
        else:
            return JsonResponse({'success': False, 'error': 'Usuario no válido'})
        
        notificacion.leida = True
        notificacion.fecha_lectura = timezone.now()
        notificacion.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def notificaciones_dropdown_api(request):
    """API para obtener las últimas notificaciones para el dropdown"""
    notificaciones_data = []
    
    if hasattr(request.user, 'cliente'):
        notificaciones = Notificacion.objects.filter(
            cliente=request.user.cliente
        ).order_by('-fecha_creacion')[:5]
    elif hasattr(request.user, 'empleado'):
        notificaciones = Notificacion.objects.filter(
            empleado=request.user.empleado,
            tipo__in=[Notificacion.CALIFICACION_RECIBIDA, Notificacion.SERVICIO_ASIGNADO]
        ).order_by('-fecha_creacion')[:5]
    else:
        notificaciones = []
    
    for notif in notificaciones:
        notificaciones_data.append({
            'id': notif.id,
            'titulo': notif.titulo,
            'mensaje': notif.mensaje[:100] + '...' if len(notif.mensaje) > 100 else notif.mensaje,
            'fecha': notif.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            'leida': notif.leida,
            'tipo': notif.tipo,
            'reserva_id': notif.reserva.id if notif.reserva else None
        })
    
    return JsonResponse({'notificaciones': notificaciones_data})
    
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
