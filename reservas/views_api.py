import json
import datetime
import uuid
import qrcode
import base64
from io import BytesIO
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from django.db.models import Q, Avg
from django.db import IntegrityError
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Servicio, Bahia, Vehiculo, MedioPago, Reserva, Recompensa
from empleados.models import Empleado
from notificaciones.models import Notificacion

class HorariosDisponiblesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            fecha_str = (request.GET.get('fecha') or request.POST.get('fecha'))
            servicio_id = (request.GET.get('servicio_id') or request.POST.get('servicio_id'))
            
            if not fecha_str or not servicio_id:
                return JsonResponse({'success': False, 'error': 'Fecha y servicio son requeridos'}, status=400)
            
            # Convertir fecha de string a objeto date
            try:
                fecha = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Formato de fecha inválido'}, status=400)
            
            # Verificar que la fecha no sea anterior a hoy
            if fecha < timezone.now().date():
                return JsonResponse({'success': False, 'error': 'No se pueden hacer reservas para fechas pasadas'}, status=400)
            
            # Obtener el servicio
            try:
                servicio = Servicio.objects.get(id=servicio_id)
            except Servicio.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Servicio no encontrado'}, status=404)
            
            # Obtener horarios disponibles para la fecha
            horarios_disponibles = []
            
            # Horario de operación (ejemplo: 8:00 AM a 6:00 PM)
            hora_inicio = datetime.time(8, 0)  # 8:00 AM
            hora_fin = datetime.time(18, 0)    # 6:00 PM
            
            # Duración del servicio en minutos
            duracion_servicio = servicio.duracion_minutos
            
            # Generar intervalos de tiempo (cada 30 minutos)
            intervalo_minutos = 30
            hora_actual = datetime.datetime.combine(fecha, hora_inicio)
            hora_limite = datetime.datetime.combine(fecha, hora_fin)
            
            while hora_actual < hora_limite:
                hora_fin_servicio = hora_actual + datetime.timedelta(minutes=duracion_servicio)
                
                # Verificar si el servicio termina antes del cierre
                if hora_fin_servicio.time() <= hora_fin:
                    # Contar bahías disponibles para este horario
                    bahias_disponibles = self.contar_bahias_disponibles(fecha, hora_actual.time(), hora_fin_servicio.time())
                    
                    if bahias_disponibles > 0:
                        horarios_disponibles.append({
                            'id': hora_actual.strftime('%H:%M'),
                            'hora': hora_actual.strftime('%H:%M'),
                            'hora_inicio': hora_actual.strftime('%H:%M'),
                            'hora_fin': hora_fin_servicio.strftime('%H:%M'),
                            'hora_formateada': f"{hora_actual.strftime('%I:%M %p')} - {hora_fin_servicio.strftime('%I:%M %p')}",
                            'bahias_disponibles': bahias_disponibles
                        })
                
                hora_actual += datetime.timedelta(minutes=intervalo_minutos)
            
            return JsonResponse({'success': True, 'horarios': horarios_disponibles})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
            
    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
    
    def contar_bahias_disponibles(self, fecha, hora_inicio, hora_fin):
        # Obtener todas las bahías activas
        bahias = Bahia.objects.filter(activa=True)
        
        # Contar bahías disponibles (no reservadas en ese horario)
        bahias_disponibles = 0
        
        for bahia in bahias:
            # Verificar si la bahía está reservada en ese horario
            reservada = Reserva.objects.filter(
                Q(bahia=bahia) & 
                Q(fecha=fecha) & 
                (
                    # La reserva existente comienza durante nuestro servicio
                    (Q(hora_inicio__gte=hora_inicio) & Q(hora_inicio__lt=hora_fin)) |
                    # La reserva existente termina durante nuestro servicio
                    (Q(hora_fin__gt=hora_inicio) & Q(hora_fin__lte=hora_fin)) |
                    # La reserva existente abarca completamente nuestro servicio
                    (Q(hora_inicio__lte=hora_inicio) & Q(hora_fin__gte=hora_fin))
                )
            ).exists()
            
            if not reservada:
                bahias_disponibles += 1
        
        return bahias_disponibles


class BahiasDisponiblesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            fecha_str = (request.GET.get('fecha') or request.POST.get('fecha'))
            hora_str = (request.GET.get('hora_id') or request.GET.get('hora') or request.POST.get('hora_id') or request.POST.get('hora'))
            servicio_id = (request.GET.get('servicio_id') or request.POST.get('servicio_id'))
            
            if not fecha_str or not hora_str or not servicio_id:
                return JsonResponse({'success': False, 'error': 'Fecha, hora y servicio son requeridos'}, status=400)
            
            # Convertir fecha y hora de string a objetos date y time
            try:
                fecha = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
                hora_inicio = datetime.datetime.strptime(hora_str, '%H:%M').time()
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Formato de fecha u hora inválido'}, status=400)
            
            # Obtener el servicio
            try:
                servicio = Servicio.objects.get(id=servicio_id)
            except Servicio.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Servicio no encontrado'}, status=404)
            
            # Calcular hora de fin del servicio
            hora_inicio_dt = datetime.datetime.combine(fecha, hora_inicio)
            hora_fin_dt = hora_inicio_dt + datetime.timedelta(minutes=servicio.duracion_minutos)
            hora_fin = hora_fin_dt.time()
            
            # Obtener bahías disponibles
            bahias_disponibles = []
            
            # Obtener todas las bahías activas
            bahias = Bahia.objects.filter(activa=True)
            
            for bahia in bahias:
                # Verificar si la bahía está reservada en ese horario
                reservada = Reserva.objects.filter(
                    Q(bahia=bahia) & 
                    Q(fecha=fecha) & 
                    (
                        # La reserva existente comienza durante nuestro servicio
                        (Q(hora_inicio__gte=hora_inicio) & Q(hora_inicio__lt=hora_fin)) |
                        # La reserva existente termina durante nuestro servicio
                        (Q(hora_fin__gt=hora_inicio) & Q(hora_fin__lte=hora_fin)) |
                        # La reserva existente abarca completamente nuestro servicio
                        (Q(hora_inicio__lte=hora_inicio) & Q(hora_fin__gte=hora_fin))
                    )
                ).exists()
                
                if not reservada:
                    bahias_disponibles.append({
                        'id': bahia.id,
                        'nombre': bahia.nombre,
                        'descripcion': bahia.descripcion
                    })
            
            return JsonResponse({'success': True, 'bahias': bahias_disponibles})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
            
    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class LavadoresDisponiblesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            fecha_str = (request.GET.get('fecha') or request.POST.get('fecha'))
            hora_str = (request.GET.get('hora_id') or request.GET.get('hora') or request.POST.get('hora_id') or request.POST.get('hora'))
            bahia_id = (request.GET.get('bahia_id') or request.POST.get('bahia_id'))
            
            if not fecha_str or not hora_str or not bahia_id:
                return JsonResponse({'success': False, 'error': 'Fecha, hora y bahía son requeridos'}, status=400)
            
            # Convertir fecha y hora de string a objetos date y time
            try:
                fecha = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
                hora_inicio = datetime.datetime.strptime(hora_str, '%H:%M').time()
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Formato de fecha u hora inválido'}, status=400)
            
            # Obtener la bahía
            try:
                bahia = Bahia.objects.get(id=bahia_id)
            except Bahia.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Bahía no encontrada'}, status=404)
            
            # Obtener lavadores disponibles
            lavadores_disponibles = []
            
            # Obtener todos los lavadores activos
            lavadores = Empleado.objects.filter(activo=True, rol='lavador')
            
            # Calcular hora de fin (asumiendo 1 hora de servicio por defecto)
            hora_inicio_dt = datetime.datetime.combine(fecha, hora_inicio)
            hora_fin_dt = hora_inicio_dt + datetime.timedelta(hours=1)  # Asumimos 1 hora por defecto
            hora_fin = hora_fin_dt.time()
            
            # Día de la semana (0: lunes, 6: domingo)
            dia_semana = fecha.weekday()
            
            for lavador in lavadores:
                # Verificar disponibilidad horaria del lavador
                disponible_horario = DisponibilidadHoraria.objects.filter(
                    empleado=lavador,
                    dia_semana=dia_semana,
                    hora_inicio__lte=hora_inicio,
                    hora_fin__gte=hora_inicio
                ).exists()
                
                if not disponible_horario:
                    continue
                
                # Verificar si el lavador está ocupado en otra reserva
                ocupado = Reserva.objects.filter(
                    Q(lavador=lavador) & 
                    Q(fecha=fecha) & 
                    (
                        # La reserva existente comienza durante nuestro servicio
                        (Q(hora_inicio__gte=hora_inicio) & Q(hora_inicio__lt=hora_fin)) |
                        # La reserva existente termina durante nuestro servicio
                        (Q(hora_fin__gt=hora_inicio) & Q(hora_fin__lte=hora_fin)) |
                        # La reserva existente abarca completamente nuestro servicio
                        (Q(hora_inicio__lte=hora_inicio) & Q(hora_fin__gte=hora_fin))
                    )
                ).exists()
                
                if not ocupado:
                    # Calcular calificación promedio
                    calificaciones = Calificacion.objects.filter(lavador=lavador)
                    calificacion_promedio = calificaciones.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
                    
                    lavadores_disponibles.append({
                        'id': lavador.id,
                        'nombre': f"{lavador.user.first_name} {lavador.user.last_name}",
                        'calificacion': round(calificacion_promedio, 1),
                        'experiencia': lavador.experiencia_anios,
                        'foto_url': lavador.foto.url if lavador.foto else None
                    })
            
            return JsonResponse({'success': True, 'lavadores': lavadores_disponibles})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class LavadorDetalleView(LoginRequiredMixin, View):
    def get(self, request, lavador_id, *args, **kwargs):
        try:
            lavador = Empleado.objects.get(id=lavador_id, activo=True, rol='lavador')
            
            # Calcular calificación promedio
            calificaciones = Calificacion.objects.filter(lavador=lavador)
            calificacion_promedio = calificaciones.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0
            
            # Obtener comentarios recientes (últimos 5)
            comentarios_recientes = []
            for calificacion in calificaciones.order_by('-fecha')[:5]:
                comentarios_recientes.append({
                    'usuario': calificacion.usuario.username,
                    'fecha': calificacion.fecha.strftime('%d/%m/%Y'),
                    'puntuacion': calificacion.puntuacion,
                    'comentario': calificacion.comentario
                })
            
            # Construir respuesta
            lavador_detalle = {
                'id': lavador.id,
                'nombre': f"{lavador.user.first_name} {lavador.user.last_name}",
                'calificacion': round(calificacion_promedio, 1),
                'experiencia': lavador.experiencia_anios,
                'especialidades': lavador.especialidades,
                'foto_url': lavador.foto.url if lavador.foto else None,
                'comentarios': comentarios_recientes
            }
            
            return JsonResponse({'success': True, 'lavador': lavador_detalle})
            
        except Empleado.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Lavador no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


class GuardarVehiculoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            
            # Validar datos requeridos
            placa = data.get('placa')
            marca = data.get('marca')
            modelo = data.get('modelo')
            
            if not placa or not marca or not modelo:
                return JsonResponse({'success': False, 'error': 'Placa, marca y modelo son requeridos'}, status=400)
            
            # Verificar si el vehículo ya existe para este usuario
            vehiculo, created = Vehiculo.objects.get_or_create(
                propietario=request.user,
                placa=placa,
                defaults={
                    'marca': marca,
                    'modelo': modelo,
                    'color': data.get('color', ''),
                    'tipo': data.get('tipo', 'automovil')
                }
            )
            
            if not created:
                # Actualizar datos del vehículo existente
                vehiculo.marca = marca
                vehiculo.modelo = modelo
                vehiculo.color = data.get('color', vehiculo.color)
                vehiculo.tipo = data.get('tipo', vehiculo.tipo)
                vehiculo.save()
            
            return JsonResponse({
                'success': True, 
                'vehiculo': {
                    'id': vehiculo.id,
                    'placa': vehiculo.placa,
                    'marca': vehiculo.marca,
                    'modelo': vehiculo.modelo,
                    'color': vehiculo.color,
                    'tipo': vehiculo.tipo
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


class CrearReservaView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            
            # Validar datos requeridos
            servicio_id = data.get('servicio_id')
            fecha_str = data.get('fecha')
            hora_str = data.get('hora_id')
            bahia_id = data.get('bahia_id')
            lavador_id = data.get('lavador_id')
            vehiculo_id = data.get('vehiculo_id')
            
            if not all([servicio_id, fecha_str, hora_str, bahia_id, lavador_id, vehiculo_id]):
                return JsonResponse({
                    'success': False, 
                    'error': 'Todos los campos son requeridos'
                }, status=400)
            
            # Convertir fecha y hora
            try:
                fecha = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
                hora_inicio = datetime.datetime.strptime(hora_str, '%H:%M').time()
                # ... existing code...
                # Componer fecha y hora en un solo DateTime, acorde al modelo Reserva
                fecha_hora_dt = datetime.datetime.combine(fecha, hora_inicio)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Formato de fecha u hora inválido'}, status=400)
            
            # Obtener objetos relacionados
            try:
                servicio = Servicio.objects.get(id=servicio_id)
                bahia = Bahia.objects.get(id=bahia_id)
                lavador = Empleado.objects.get(id=lavador_id)
                vehiculo = Vehiculo.objects.get(id=vehiculo_id, cliente=request.user.cliente)
                medio_pago = None
            except (Servicio.DoesNotExist, Bahia.DoesNotExist, 
                    Empleado.DoesNotExist, Vehiculo.DoesNotExist) as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=404)
            
            # Calcular hora de fin
            hora_inicio_dt = datetime.datetime.combine(fecha, hora_inicio)
            hora_fin_dt = hora_inicio_dt + datetime.timedelta(minutes=servicio.duracion_minutos)
            hora_fin = hora_fin_dt.time()
            
            # Verificar disponibilidad nuevamente
            # (Bahía disponible)
            bahia_ocupada = Reserva.objects.filter(
                bahia=bahia,
                fecha_hora=fecha_hora_dt
            ).exists()
            if bahia_ocupada:
                return JsonResponse({'success': False, 'error': 'La bahía ya no está disponible'}, status=400)
            # (Lavador disponible)
            lavador_ocupado = Reserva.objects.filter(
                lavador=lavador,
                fecha_hora=fecha_hora_dt
            ).exists()
            if lavador_ocupado:
                return JsonResponse({'success': False, 'error': 'El lavador ya no está disponible'}, status=400)
            # Crear la reserva
            try:
                reserva = Reserva.objects.create(
                    cliente=request.user.cliente,
                    servicio=servicio,
                    bahia=bahia,
                    lavador=lavador,
                    vehiculo=vehiculo,
                    fecha_hora=fecha_hora_dt,
                    precio_final=servicio.precio,
                    medio_pago=medio_pago,
                    estado=Reserva.PENDIENTE
                )
            except IntegrityError:
                return JsonResponse({'success': False, 'error': 'Esta bahía ya está reservada para la fecha y hora seleccionada. Por favor, selecciona otra bahía u horario.'}, status=400)
            
            # Aplicar redención de puntos mediante una Recompensa (si se solicitó)
            usar_puntos = bool(data.get('usar_puntos', False))
            recompensa_id = data.get('recompensa_id') or data.get('recompensa_seleccionada')
            if usar_puntos and recompensa_id:
                try:
                    recompensa = Recompensa.objects.get(id=recompensa_id, activo=True)
                except Recompensa.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'La recompensa seleccionada no existe o está inactiva'}, status=400)
                # Validar que la recompensa aplica al servicio elegido
                if recompensa.servicio_id != servicio.id:
                    return JsonResponse({'success': False, 'error': 'La recompensa no aplica para el servicio seleccionado'}, status=400)
                puntos_req = recompensa.puntos_requeridos
                # Validar saldo de puntos
                if request.user.cliente.saldo_puntos < puntos_req:
                    return JsonResponse({'success': False, 'error': 'No tienes puntos suficientes para esta recompensa'}, status=400)
                # Calcular descuento según el tipo de recompensa y el precio del servicio
                descuento = recompensa.calcular_descuento(servicio.precio) or 0
                # Redimir puntos
                if not request.user.cliente.redimir_puntos(puntos_req):
                    return JsonResponse({'success': False, 'error': 'No fue posible redimir los puntos'}, status=400)
                # Aplicar cambios a la reserva
                reserva.descuento_aplicado = descuento
                reserva.puntos_redimidos = puntos_req
                reserva.recompensa_aplicada = recompensa.nombre
                final = servicio.precio - descuento
                reserva.precio_final = final if final > 0 else 0
                reserva.save(update_fields=['descuento_aplicado', 'puntos_redimidos', 'recompensa_aplicada', 'precio_final'])
            
            # Auto-confirmar la reserva y crear notificación de confirmación
            try:
                if reserva.confirmar():
                    Notificacion.objects.create(
                        cliente=request.user.cliente,
                        reserva=reserva,
                        tipo=Notificacion.RESERVA_CONFIRMADA,
                        titulo='Reserva Confirmada',
                        mensaje=f"Tu reserva para {reserva.servicio.nombre} el {reserva.fecha_hora.strftime('%d/%m/%Y')} a las {reserva.fecha_hora.strftime('%H:%M')} ha sido confirmada."
                    )
            except Exception:
                pass
            
            return JsonResponse({
                'success': True, 
                'reserva': {
                    'id': reserva.id,
                    'fecha': reserva.fecha_hora.strftime('%d/%m/%Y'),
                    'hora': reserva.fecha_hora.strftime('%I:%M %p'),
                    'servicio': reserva.servicio.nombre,
                    'precio_final': float(reserva.precio_final if reserva.precio_final is not None else servicio.precio),
                    'descuento_aplicado': float(reserva.descuento_aplicado),
                    'puntos_redimidos': reserva.puntos_redimidos,
                    'recompensa_aplicada': reserva.recompensa_aplicada,
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


class GenerarQRView(LoginRequiredMixin, View):
    def get(self, request, reserva_id, *args, **kwargs):
        try:
            # Obtener la reserva
            reserva = Reserva.objects.get(id=reserva_id, cliente=request.user.cliente)
            
            # Generar datos para el QR
            qr_data = {
                'reserva_id': reserva.id,
                'codigo_acceso': reserva.codigo_acceso,
                'cliente': f"{reserva.cliente.first_name} {reserva.cliente.last_name}",
                'fecha': reserva.fecha.strftime('%d/%m/%Y'),
                'hora_inicio': reserva.hora_inicio.strftime('%H:%M'),
                'hora_fin': reserva.hora_fin.strftime('%H:%M'),
                'servicio': reserva.servicio.nombre,
                'bahia': reserva.bahia.nombre,
                'lavador': f"{reserva.lavador.user.first_name} {reserva.lavador.user.last_name}",
                'vehiculo': {
                    'placa': reserva.vehiculo.placa,
                    'marca': reserva.vehiculo.marca,
                    'modelo': reserva.vehiculo.modelo,
                    'color': reserva.vehiculo.color
                },
                'precio': float(reserva.precio),
                'medio_pago': (reserva.medio_pago.nombre if reserva.medio_pago else 'No especificado')
            }
            
            # Generar QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a base64
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Construir comprobante
            comprobante = {
                'reserva_id': reserva.id,
                'codigo_acceso': reserva.codigo_acceso,
                'qr_base64': qr_base64,
                'cliente': f"{reserva.cliente.first_name} {reserva.cliente.last_name}",
                'fecha': reserva.fecha.strftime('%d/%m/%Y'),
                'hora': f"{reserva.hora_inicio.strftime('%I:%M %p')} - {reserva.hora_fin.strftime('%I:%M %p')}",
                'servicio': reserva.servicio.nombre,
                'bahia': reserva.bahia.nombre,
                'lavador': f"{reserva.lavador.user.first_name} {reserva.lavador.user.last_name}",
                'vehiculo': {
                    'placa': reserva.vehiculo.placa,
                    'marca': reserva.vehiculo.marca,
                    'modelo': reserva.vehiculo.modelo,
                    'color': reserva.vehiculo.color
                },
                'precio': float(reserva.precio),
                'medio_pago': (reserva.medio_pago.nombre if reserva.medio_pago else 'No especificado')
            }
            
            return JsonResponse({'success': True, 'comprobante': comprobante})
            
        except Reserva.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Reserva no encontrada'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verificar_placa_unica(request):
    """
    Endpoint para verificar si una placa ya existe en la base de datos
    """
    try:
        # Usar request.data en lugar de request.body para DRF
        placa = request.data.get('placa', '').strip().upper()
        
        if not placa:
            return Response({
                'success': False, 
                'error': 'La placa es requerida'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si ya existe un vehículo con la misma placa
        from .models import Vehiculo
        vehiculo_existente = Vehiculo.objects.filter(placa=placa).first()
        
        if vehiculo_existente:
            # Verificar si pertenece al cliente actual
            cliente_actual = request.user.cliente
            if vehiculo_existente.cliente == cliente_actual:
                return Response({
                    'success': True,
                    'existe': True,
                    'es_propio': True,
                    'mensaje': 'Ya tienes un vehículo registrado con esta placa'
                })
            else:
                return Response({
                    'success': True,
                    'existe': True,
                    'es_propio': False,
                    'mensaje': 'Esta placa ya está registrada para otro cliente'
                })
        else:
            return Response({
                'success': True,
                'existe': False,
                'es_propio': False,
                'mensaje': 'La placa está disponible'
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)