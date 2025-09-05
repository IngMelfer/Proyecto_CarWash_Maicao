from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from .models import Servicio, Reserva, Vehiculo, HorarioDisponible
from .serializers import ServicioSerializer, ReservaSerializer, ReservaUpdateSerializer
from notificaciones.models import Notificacion
from clientes.models import Cliente, HistorialServicio
import json
from datetime import datetime, timedelta

# Create your views here.

# Vistas basadas en clases para plantillas HTML
class ReservarTurnoView(LoginRequiredMixin, TemplateView):
    template_name = 'reservas/reservar_turno.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['servicios'] = Servicio.objects.filter(activo=True)
        context['vehiculos'] = Vehiculo.objects.filter(cliente=self.request.user.cliente)
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            # Obtener datos del formulario
            servicio_id = request.POST.get('servicio')
            fecha_str = request.POST.get('fecha')
            hora_str = request.POST.get('hora')
            vehiculo_id = request.POST.get('vehiculo')
            notas = request.POST.get('notas', '')
            
            # Validar datos
            if not all([servicio_id, fecha_str, hora_str, vehiculo_id]):
                messages.error(request, 'Por favor complete todos los campos requeridos.')
                return redirect('reservas:reservar_turno')
            
            # Obtener objetos
            servicio = get_object_or_404(Servicio, id=servicio_id)
            vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id, cliente=request.user.cliente)
            
            # Convertir fecha y hora
            fecha_hora = datetime.strptime(f'{fecha_str} {hora_str}', '%Y-%m-%d %H:%M')
            fecha_hora = timezone.make_aware(fecha_hora)
            
            # Verificar que la fecha no sea en el pasado
            if fecha_hora < timezone.now():
                messages.error(request, 'No se pueden hacer reservas para fechas pasadas.')
                return redirect('reservas:reservar_turno')
            
            # Verificar disponibilidad
            horario = HorarioDisponible.objects.filter(
                fecha=fecha_hora.date(),
                hora_inicio__lte=fecha_hora.time(),
                hora_fin__gt=fecha_hora.time(),
                disponible=True
            ).first()
            
            if not horario or horario.esta_lleno:
                messages.error(request, 'El horario seleccionado no está disponible.')
                return redirect('reservas:reservar_turno')
            
            # Crear la reserva
            reserva = Reserva.objects.create(
                cliente=request.user.cliente,
                servicio=servicio,
                fecha_hora=fecha_hora,
                notas=notas,
                estado=Reserva.PENDIENTE
            )
            
            # Incrementar contador de reservas en el horario
            horario.incrementar_reservas()
            
            # Crear notificación
            Notificacion.objects.create(
                cliente=request.user.cliente,
                tipo=Notificacion.RESERVA_CREADA,
                titulo='Reserva Creada',
                mensaje=f'Tu reserva para el servicio {servicio.nombre} ha sido creada para el {fecha_hora.strftime("%d/%m/%Y a las %H:%M")}. Recibirás una confirmación pronto.',
            )
            
            messages.success(request, 'Reserva creada exitosamente. Recibirás una confirmación pronto.')
            return redirect('reservas:mis_turnos')
            
        except Exception as e:
            messages.error(request, f'Error al crear la reserva: {str(e)}')
            return redirect('reservas:reservar_turno')


class MisTurnosView(LoginRequiredMixin, TemplateView):
    template_name = 'reservas/mis_turnos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente = self.request.user.cliente
        
        # Obtener reservas del cliente
        proximas = Reserva.objects.filter(
            cliente=cliente,
            fecha_hora__gte=timezone.now(),
            estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA]
        ).order_by('fecha_hora')
        
        pasadas = Reserva.objects.filter(
            cliente=cliente,
            estado=Reserva.COMPLETADA
        ).order_by('-fecha_hora')
        
        canceladas = Reserva.objects.filter(
            cliente=cliente,
            estado=Reserva.CANCELADA
        ).order_by('-fecha_hora')
        
        context['proximas'] = proximas
        context['pasadas'] = pasadas
        context['canceladas'] = canceladas
        
        return context


class CancelarTurnoView(LoginRequiredMixin, View):
    def post(self, request, turno_id, *args, **kwargs):
        reserva = get_object_or_404(Reserva, id=turno_id, cliente=request.user.cliente)
        motivo = request.POST.get('motivo', '')
        
        # Verificar si la reserva puede ser cancelada
        if reserva.estado in [Reserva.EN_PROCESO, Reserva.COMPLETADA]:
            messages.error(request, 'No se puede cancelar una reserva en proceso o completada.')
            return redirect('mis_turnos')
        
        # Verificar si la cancelación es con menos de 24 horas de anticipación
        horas_anticipacion = (reserva.fecha_hora - timezone.now()).total_seconds() / 3600
        cargo_cancelacion = horas_anticipacion < 24
        
        # Cancelar la reserva
        reserva.estado = Reserva.CANCELADA
        reserva.notas = f"{reserva.notas}\n\nMotivo de cancelación: {motivo}"
        reserva.save(update_fields=['estado', 'notas'])
        
        # Decrementar contador de reservas en el horario si existe
        horario = HorarioDisponible.objects.filter(
            fecha=reserva.fecha_hora.date(),
            hora_inicio__lte=reserva.fecha_hora.time(),
            hora_fin__gt=reserva.fecha_hora.time()
        ).first()
        
        if horario:
            horario.decrementar_reservas()
        
        # Crear notificación
        mensaje = f'Tu reserva para el servicio {reserva.servicio.nombre} programada para el {reserva.fecha_hora.strftime("%d/%m/%Y a las %H:%M")} ha sido cancelada.'
        if cargo_cancelacion:
            mensaje += ' Se ha aplicado un cargo por cancelación tardía.'
        
        Notificacion.objects.create(
            cliente=request.user.cliente,
            tipo=Notificacion.RESERVA_CANCELADA,
            titulo='Reserva Cancelada',
            mensaje=mensaje,
        )
        
        messages.success(request, 'Reserva cancelada exitosamente.')
        if cargo_cancelacion:
            messages.warning(request, 'Se ha aplicado un cargo por cancelación tardía.')
            
        return redirect('mis_turnos')


class CalificarTurnoView(LoginRequiredMixin, View):
    template_name = 'reservas/calificar_turno.html'
    
    def get(self, request, turno_id, *args, **kwargs):
        reserva = get_object_or_404(Reserva, id=turno_id, cliente=request.user.cliente)
        
        # Verificar si la reserva puede ser calificada
        if reserva.estado != Reserva.COMPLETADA:
            messages.error(request, 'Solo se pueden calificar servicios completados.')
            return redirect('mis_turnos')
        
        return render(request, self.template_name, {'reserva': reserva})
    
    def post(self, request, turno_id, *args, **kwargs):
        reserva = get_object_or_404(Reserva, id=turno_id, cliente=request.user.cliente)
        
        # Verificar si la reserva puede ser calificada
        if reserva.estado != Reserva.COMPLETADA:
            messages.error(request, 'Solo se pueden calificar servicios completados.')
            return redirect('mis_turnos')
        
        # Obtener datos del formulario
        puntuacion = request.POST.get('puntuacion')
        comentario = request.POST.get('comentario', '')
        
        try:
            puntuacion = int(puntuacion)
            if not (1 <= puntuacion <= 5):
                raise ValueError('La calificación debe estar entre 1 y 5')
        except (ValueError, TypeError):
            messages.error(request, 'La calificación debe ser un número entre 1 y 5.')
            return render(request, self.template_name, {'reserva': reserva})
        
        # Buscar si ya existe un historial para esta reserva
        historial = HistorialServicio.objects.filter(
            cliente=request.user.cliente,
            servicio=reserva.servicio.nombre,
            fecha_servicio__date=reserva.fecha_hora.date()
        ).first()
        
        if historial:
            # Actualizar calificación y comentario
            historial.calificacion = puntuacion
            historial.comentarios = comentario
            historial.save(update_fields=['calificacion', 'comentarios'])
        else:
            # Crear nuevo historial con calificación
            HistorialServicio.objects.create(
                cliente=request.user.cliente,
                servicio=reserva.servicio.nombre,
                descripcion=reserva.servicio.descripcion,
                fecha_servicio=reserva.fecha_hora,
                monto=reserva.servicio.precio,
                puntos_ganados=reserva.servicio.puntos_otorgados,
                calificacion=puntuacion,
                comentarios=comentario
            )
        
        messages.success(request, 'Gracias por calificar nuestro servicio.')
        return redirect('mis_turnos')


class ObtenerHorariosDisponiblesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            fecha_str = request.GET.get('fecha')
            servicio_id = request.GET.get('servicio_id')
            
            if not fecha_str or not servicio_id:
                return JsonResponse({'error': 'Parámetros incompletos'}, status=400)
            
            # Convertir fecha
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)
            
            # Verificar que la fecha no sea en el pasado
            if fecha < timezone.now().date():
                return JsonResponse({'error': 'No se pueden hacer reservas para fechas pasadas'}, status=400)
            
            # Obtener servicio
            servicio = get_object_or_404(Servicio, id=servicio_id)
            
            # Obtener horarios disponibles para esa fecha
            horarios_disponibles = HorarioDisponible.objects.filter(
                fecha=fecha,
                disponible=True
            ).exclude(esta_lleno=True).order_by('hora_inicio')
            
            # Si no hay horarios específicos para esa fecha, usar la disponibilidad general
            if not horarios_disponibles:
                # Obtener el día de la semana (0-6, donde 0 es lunes)
                dia_semana = fecha.weekday()
                
                # Buscar disponibilidad general para ese día
                disponibilidad_general = DisponibilidadHoraria.objects.filter(
                    dia_semana=dia_semana,
                    activo=True
                ).order_by('hora_inicio')
                
                # Crear horarios disponibles basados en la disponibilidad general
                horarios = []
                for disp in disponibilidad_general:
                    # Crear intervalos de 30 minutos
                    hora_actual = disp.hora_inicio
                    while hora_actual < disp.hora_fin:
                        hora_fin = (datetime.combine(fecha, hora_actual) + timedelta(minutes=30)).time()
                        if hora_fin <= disp.hora_fin:
                            horarios.append({
                                'hora_inicio': hora_actual.strftime('%H:%M'),
                                'hora_fin': hora_fin.strftime('%H:%M'),
                                'disponible': True
                            })
                        hora_actual = hora_fin
                
                # Filtrar horarios que ya tienen reservas
                for horario in horarios:
                    hora_inicio = datetime.strptime(horario['hora_inicio'], '%H:%M').time()
                    fecha_hora = timezone.make_aware(datetime.combine(fecha, hora_inicio))
                    
                    # Contar reservas existentes para esa fecha y hora
                    reservas_count = Reserva.objects.filter(
                        fecha_hora=fecha_hora,
                        estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
                    ).count()
                    
                    # Marcar como no disponible si está lleno
                    if reservas_count >= disp.capacidad_maxima:
                        horario['disponible'] = False
            else:
                # Usar los horarios específicos de la fecha
                horarios = [{
                    'hora_inicio': h.hora_inicio.strftime('%H:%M'),
                    'hora_fin': h.hora_fin.strftime('%H:%M'),
                    'disponible': not h.esta_lleno
                } for h in horarios_disponibles]
            
            return JsonResponse({'horarios': horarios})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ServicioViewSet(viewsets.ModelViewSet):
    """ViewSet para el modelo Servicio"""
    queryset = Servicio.objects.filter(activo=True)
    serializer_class = ServicioSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'precio', 'duracion_minutos']
    
    def get_permissions(self):
        """Definir permisos según la acción"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class ReservaViewSet(viewsets.ModelViewSet):
    """ViewSet para el modelo Reserva"""
    serializer_class = ReservaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['servicio__nombre', 'estado']
    ordering_fields = ['fecha_hora', 'estado']
    
    def get_queryset(self):
        """Filtrar reservas según el tipo de usuario"""
        usuario = self.request.user
        
        # Si es admin, mostrar todas las reservas
        if usuario.is_staff:
            return Reserva.objects.all()
        
        # Si es cliente, mostrar solo sus reservas
        try:
            cliente = Cliente.objects.get(usuario=usuario)
            return Reserva.objects.filter(cliente=cliente)
        except Cliente.DoesNotExist:
            return Reserva.objects.none()
    
    def get_serializer_class(self):
        """Seleccionar el serializer según la acción"""
        if self.action in ['update', 'partial_update']:
            return ReservaUpdateSerializer
        return ReservaSerializer
    
    def get_permissions(self):
        """Definir permisos según la acción"""
        if self.action in ['destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Crear una reserva y enviar notificación"""
        reserva = serializer.save()
        
        # Crear notificación para el cliente
        Notificacion.objects.create(
            cliente=reserva.cliente,
            tipo=Notificacion.RESERVA_CREADA,
            titulo='Reserva Creada',
            mensaje=f'Tu reserva para el servicio {reserva.servicio.nombre} ha sido creada exitosamente para el {reserva.fecha_hora.strftime("%d/%m/%Y a las %H:%M")}.',
        )
    
    def perform_update(self, serializer):
        """Actualizar una reserva y enviar notificación"""
        estado_anterior = serializer.instance.estado
        reserva = serializer.save()
        
        # Si el estado cambió, enviar notificación
        if estado_anterior != reserva.estado:
            tipo_notificacion = None
            titulo = None
            mensaje = None
            
            if reserva.estado == Reserva.CONFIRMADA:
                tipo_notificacion = Notificacion.RESERVA_CONFIRMADA
                titulo = 'Reserva Confirmada'
                mensaje = f'Tu reserva para el servicio {reserva.servicio.nombre} ha sido confirmada para el {reserva.fecha_hora.strftime("%d/%m/%Y a las %H:%M")}. ¡Te esperamos!'
            
            elif reserva.estado == Reserva.CANCELADA:
                tipo_notificacion = Notificacion.RESERVA_CANCELADA
                titulo = 'Reserva Cancelada'
                mensaje = f'Tu reserva para el servicio {reserva.servicio.nombre} programada para el {reserva.fecha_hora.strftime("%d/%m/%Y a las %H:%M")} ha sido cancelada.'
            
            elif reserva.estado == Reserva.EN_PROCESO:
                tipo_notificacion = Notificacion.SERVICIO_INICIADO
                titulo = 'Servicio Iniciado'
                mensaje = f'Tu servicio de {reserva.servicio.nombre} ha iniciado.'
            
            elif reserva.estado == Reserva.COMPLETADA:
                tipo_notificacion = Notificacion.SERVICIO_FINALIZADO
                titulo = 'Servicio Completado'
                mensaje = f'Tu servicio de {reserva.servicio.nombre} ha sido completado exitosamente.'
                
                # Crear registro en historial de servicios
                HistorialServicio.objects.create(
                    cliente=reserva.cliente,
                    servicio=reserva.servicio.nombre,
                    descripcion=reserva.servicio.descripcion,
                    fecha_servicio=timezone.now(),
                    monto=reserva.servicio.precio,
                    puntos_ganados=reserva.servicio.puntos_otorgados,
                    comentarios=reserva.notas
                )
                
                # Acumular puntos al cliente
                if reserva.servicio.puntos_otorgados > 0:
                    reserva.cliente.acumular_puntos(reserva.servicio.puntos_otorgados)
                    
                    # Notificación de puntos acumulados
                    Notificacion.objects.create(
                        cliente=reserva.cliente,
                        tipo=Notificacion.PUNTOS_ACUMULADOS,
                        titulo='Puntos Acumulados',
                        mensaje=f'Has acumulado {reserva.servicio.puntos_otorgados} puntos por tu servicio de {reserva.servicio.nombre}. Tu saldo actual es de {reserva.cliente.saldo_puntos} puntos.',
                    )
            
            # Crear notificación si hay cambio de estado
            if tipo_notificacion and titulo and mensaje:
                Notificacion.objects.create(
                    cliente=reserva.cliente,
                    tipo=tipo_notificacion,
                    titulo=titulo,
                    mensaje=mensaje,
                )
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancelar una reserva"""
        reserva = self.get_object()
        
        # Verificar si la reserva puede ser cancelada
        if reserva.estado in [Reserva.EN_PROCESO, Reserva.COMPLETADA]:
            return Response({
                'error': 'No se puede cancelar una reserva en proceso o completada'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Cancelar la reserva
        reserva.estado = Reserva.CANCELADA
        reserva.save(update_fields=['estado'])
        
        # Crear notificación
        Notificacion.objects.create(
            cliente=reserva.cliente,
            tipo=Notificacion.RESERVA_CANCELADA,
            titulo='Reserva Cancelada',
            mensaje=f'Tu reserva para el servicio {reserva.servicio.nombre} programada para el {reserva.fecha_hora.strftime("%d/%m/%Y a las %H:%M")} ha sido cancelada.',
        )
        
        return Response({
            'mensaje': 'Reserva cancelada exitosamente'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        """Confirmar una reserva"""
        reserva = self.get_object()
        
        # Verificar si la reserva puede ser confirmada
        if reserva.estado != Reserva.PENDIENTE:
            return Response({
                'error': 'Solo se pueden confirmar reservas pendientes'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Confirmar la reserva
        reserva.estado = Reserva.CONFIRMADA
        reserva.save(update_fields=['estado'])
        
        # Crear notificación
        Notificacion.objects.create(
            cliente=reserva.cliente,
            tipo=Notificacion.RESERVA_CONFIRMADA,
            titulo='Reserva Confirmada',
            mensaje=f'Tu reserva para el servicio {reserva.servicio.nombre} ha sido confirmada para el {reserva.fecha_hora.strftime("%d/%m/%Y a las %H:%M")}. ¡Te esperamos!',
        )
        
        return Response({
            'mensaje': 'Reserva confirmada exitosamente'
        }, status=status.HTTP_200_OK)
