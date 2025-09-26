from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from .models import Reserva
from empleados.models import Calificacion, Empleado
from notificaciones.models import Notificacion
import json


class CalificarLavadorView(LoginRequiredMixin, View):
    """
    Vista para que el cliente califique al lavador después de completar el servicio.
    """
    
    def get(self, request, reserva_id):
        """
        Muestra el formulario de calificación para una reserva específica.
        """
        reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user.cliente)
        
        # Verificar que la reserva esté completada
        if reserva.estado != Reserva.COMPLETADA:
            messages.error(request, 'Solo puedes calificar servicios que hayan sido completados.')
            return redirect('clientes:dashboard')
        
        # Verificar que tenga lavador asignado
        if not reserva.lavador:
            messages.error(request, 'Esta reserva no tiene un lavador asignado para calificar.')
            return redirect('clientes:dashboard')
        
        # Verificar si ya fue calificado
        calificacion_existente = Calificacion.objects.filter(
            empleado=reserva.lavador,
            servicio=reserva.servicio,
            cliente=request.user.cliente
        ).first()
        
        if calificacion_existente:
            messages.info(request, 'Ya has calificado este servicio anteriormente.')
            return redirect('clientes:dashboard')
        
        context = {
            'reserva': reserva,
            'lavador': reserva.lavador,
            'servicio': reserva.servicio,
        }
        
        return render(request, 'reservas/calificar_lavador.html', context)
    
    def post(self, request, reserva_id):
        """
        Procesa la calificación del lavador.
        """
        reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user.cliente)
        
        # Verificaciones de seguridad
        if reserva.estado != Reserva.COMPLETADA:
            return JsonResponse({'success': False, 'error': 'Solo puedes calificar servicios completados.'})
        
        if not reserva.lavador:
            return JsonResponse({'success': False, 'error': 'Esta reserva no tiene un lavador asignado.'})
        
        # Verificar si ya fue calificado
        calificacion_existente = Calificacion.objects.filter(
            empleado=reserva.lavador,
            servicio=reserva.servicio,
            cliente=request.user.cliente
        ).first()
        
        if calificacion_existente:
            return JsonResponse({'success': False, 'error': 'Ya has calificado este servicio.'})
        
        try:
            # Obtener datos del formulario
            puntuacion = int(request.POST.get('puntuacion', 0))
            comentario = request.POST.get('comentario', '').strip()
            
            # Validar puntuación
            if puntuacion < 1 or puntuacion > 5:
                return JsonResponse({'success': False, 'error': 'La puntuación debe estar entre 1 y 5 estrellas.'})
            
            # Crear la calificación
            calificacion = Calificacion.objects.create(
                empleado=reserva.lavador,
                servicio=reserva.servicio,
                cliente=request.user.cliente,
                puntuacion=puntuacion,
                comentario=comentario
            )
            
            # Marcar la reserva como calificada
            reserva.calificacion_solicitada = True
            reserva.save(update_fields=['calificacion_solicitada'])
            
            # Marcar la notificación como leída si existe
            notificacion = Notificacion.objects.filter(
                cliente=request.user.cliente,
                reserva=reserva,
                tipo=Notificacion.SERVICIO_FINALIZADO
            ).first()
            
            if notificacion:
                notificacion.marcar_como_leida()
            
            # Crear notificación para el lavador
            # Nota: Las notificaciones se asocian al cliente de la reserva pero se filtran por lavador en las vistas
            mensaje_lavador = f"""¡Has recibido una nueva calificación!

Has sido calificado con {puntuacion} estrella{'s' if puntuacion != 1 else ''} por el servicio de {reserva.servicio.nombre}.

Cliente: {reserva.cliente.nombre_completo()}

{f'Comentario: "{comentario}"' if comentario else 'Sin comentarios adicionales.'}

¡Sigue así, excelente trabajo!"""
            
            # Crear la notificación asociada al cliente de la reserva
            # Las vistas de empleados filtrarán por reserva.lavador para mostrar solo las del empleado
            Notificacion.objects.create(
                cliente=reserva.cliente,  # Asociamos al cliente de la reserva
                reserva=reserva,
                tipo=Notificacion.CALIFICACION_RECIBIDA,
                titulo=f'Nueva calificación recibida - {puntuacion} estrella{"s" if puntuacion != 1 else ""}',
                mensaje=mensaje_lavador
            )
            
            return JsonResponse({
                'success': True, 
                'message': f'¡Gracias por tu calificación de {puntuacion} estrella{"s" if puntuacion != 1 else ""}!',
                'redirect_url': reverse('clientes:dashboard')
            })
            
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Puntuación inválida.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error al procesar la calificación: {str(e)}'})


@login_required
def ver_calificaciones_lavador(request, lavador_id):
    """
    Vista para ver las calificaciones de un lavador específico.
    """
    lavador = get_object_or_404(Empleado, id=lavador_id, rol=Empleado.ROL_LAVADOR)
    
    calificaciones = Calificacion.objects.filter(empleado=lavador).order_by('-fecha_calificacion')
    promedio = lavador.promedio_calificacion()
    total_calificaciones = calificaciones.count()
    
    context = {
        'lavador': lavador,
        'calificaciones': calificaciones,
        'promedio_calificacion': promedio,
        'total_calificaciones': total_calificaciones,
    }
    
    return render(request, 'reservas/calificaciones_lavador.html', context)