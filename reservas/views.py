from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework import status, viewsets, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from .models import Servicio, Reserva, Vehiculo, HorarioDisponible, Bahia, DisponibilidadHoraria, MedioPago
from .serializers import ServicioSerializer, ReservaSerializer, ReservaUpdateSerializer, BahiaSerializer
from notificaciones.models import Notificacion
from clientes.models import Cliente, HistorialServicio
import json
import uuid
import requests
import hashlib
import hmac
import base64
from datetime import datetime, timedelta

# Create your views here.

class ProcesarPagoView(LoginRequiredMixin, View):
    """
    Vista para procesar pagos con pasarelas colombianas.
    """
    def get(self, request, reserva_id, *args, **kwargs):
        # Obtener la reserva
        reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user.cliente)
        
        # Verificar que la reserva esté pendiente
        if reserva.estado != Reserva.PENDIENTE:
            messages.error(request, 'Solo se pueden procesar pagos de reservas pendientes.')
            return redirect('reservas:mis_turnos')
        
        # Obtener el medio de pago
        medio_pago = reserva.medio_pago
        
        # Verificar que el medio de pago sea una pasarela
        if not medio_pago.es_pasarela():
            messages.error(request, 'El medio de pago seleccionado no es una pasarela de pago en línea.')
            return redirect('reservas:mis_turnos')
        
        # Preparar datos para la pasarela
        monto = reserva.servicio.precio
        referencia = f"RESERVA-{reserva.id}-{uuid.uuid4().hex[:8]}"
        descripcion = f"Reserva de {reserva.servicio.nombre} - {reserva.fecha_hora.strftime('%Y-%m-%d %H:%M')}"
        
        # Guardar la referencia en la reserva para validar el callback
        reserva.referencia_pago = referencia
        reserva.save(update_fields=['referencia_pago'])
        
        # Procesar según el tipo de pasarela
        if medio_pago.tipo == MedioPago.WOMPI:
            return self._procesar_wompi(request, reserva, medio_pago, monto, referencia, descripcion)
        elif medio_pago.tipo == MedioPago.PAYU:
            return self._procesar_payu(request, reserva, medio_pago, monto, referencia, descripcion)
        elif medio_pago.tipo == MedioPago.EPAYCO:
            return self._procesar_epayco(request, reserva, medio_pago, monto, referencia, descripcion)
        elif medio_pago.tipo == MedioPago.NEQUI:
            return self._procesar_nequi(request, reserva, medio_pago, monto, referencia, descripcion)
        elif medio_pago.tipo == MedioPago.PSE:
            return self._procesar_pse(request, reserva, medio_pago, monto, referencia, descripcion)
        else:
            messages.error(request, 'Pasarela de pago no soportada.')
            return redirect('reservas:mis_turnos')
    
    def _procesar_wompi(self, request, reserva, medio_pago, monto, referencia, descripcion):
        """
        Procesa el pago con Wompi.
        """
        # URL de la API de Wompi (sandbox o producción)
        base_url = "https://sandbox.wompi.co/v1" if medio_pago.sandbox else "https://production.wompi.co/v1"
        
        # URL de retorno después del pago
        redirect_url = request.build_absolute_uri(reverse('reservas:confirmar_pago', args=[reserva.id]))
        
        # Datos para el formulario de pago
        context = {
            'reserva': reserva,
            'medio_pago': medio_pago,
            'monto': monto,
            'referencia': referencia,
            'descripcion': descripcion,
            'base_url': base_url,
            'redirect_url': redirect_url,
            'public_key': medio_pago.api_key,
        }
        
        return render(request, 'reservas/pasarelas/wompi_checkout.html', context)
    
    def _procesar_payu(self, request, reserva, medio_pago, monto, referencia, descripcion):
        """
        Procesa el pago con PayU.
        """
        # URL de la API de PayU (sandbox o producción)
        base_url = "https://sandbox.api.payulatam.com/payments-api" if medio_pago.sandbox else "https://api.payulatam.com/payments-api"
        
        # URL de retorno después del pago
        redirect_url = request.build_absolute_uri(reverse('reservas:confirmar_pago', args=[reserva.id]))
        
        # Datos para el formulario de pago
        context = {
            'reserva': reserva,
            'medio_pago': medio_pago,
            'monto': monto,
            'referencia': referencia,
            'descripcion': descripcion,
            'base_url': base_url,
            'redirect_url': redirect_url,
            'merchant_id': medio_pago.merchant_id,
            'api_key': medio_pago.api_key,
        }
        
        return render(request, 'reservas/pasarelas/payu_checkout.html', context)
    
    def _procesar_epayco(self, request, reserva, medio_pago, monto, referencia, descripcion):
        """
        Procesa el pago con ePayco.
        """
        # URL de la API de ePayco (sandbox o producción)
        base_url = "https://secure.sandbox.epayco.co" if medio_pago.sandbox else "https://secure.epayco.co"
        
        # URL de retorno después del pago
        redirect_url = request.build_absolute_uri(reverse('reservas:confirmar_pago', args=[reserva.id]))
        
        # Datos para el formulario de pago
        context = {
            'reserva': reserva,
            'medio_pago': medio_pago,
            'monto': monto,
            'referencia': referencia,
            'descripcion': descripcion,
            'base_url': base_url,
            'redirect_url': redirect_url,
            'public_key': medio_pago.api_key,
        }
        
        return render(request, 'reservas/pasarelas/epayco_checkout.html', context)
    
    def _procesar_nequi(self, request, reserva, medio_pago, monto, referencia, descripcion):
        """
        Procesa el pago con Nequi (simulación).
        """
        # Datos para la plantilla de simulación de pago
        context = {
            'reserva': reserva,
            'medio_pago': medio_pago,
            'monto': monto,
            'referencia': referencia,
            'descripcion': descripcion,
        }
        
        return render(request, 'reservas/pasarelas/nequi_checkout.html', context)
    
    def _procesar_pse(self, request, reserva, medio_pago, monto, referencia, descripcion):
        """
        Procesa el pago con PSE (a través de PayU).
        """
        return self._procesar_payu(request, reserva, medio_pago, monto, referencia, descripcion)


class ConfirmarPagoView(LoginRequiredMixin, View):
    """
    Vista para confirmar el pago después de redirigir desde la pasarela.
    """
    def get(self, request, reserva_id, *args, **kwargs):
        # Obtener la reserva
        reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user.cliente)
        
        # Verificar el estado de la transacción según la pasarela
        medio_pago = reserva.medio_pago
        
        if medio_pago.tipo == MedioPago.WOMPI:
            return self._confirmar_wompi(request, reserva)
        elif medio_pago.tipo == MedioPago.PAYU:
            return self._confirmar_payu(request, reserva)
        elif medio_pago.tipo == MedioPago.EPAYCO:
            return self._confirmar_epayco(request, reserva)
        elif medio_pago.tipo == MedioPago.NEQUI:
            return self._confirmar_nequi(request, reserva)  # Usar método específico para Nequi
        elif medio_pago.tipo == MedioPago.PSE:
            return self._confirmar_payu(request, reserva)  # PSE usa PayU
        else:
            messages.error(request, 'Pasarela de pago no soportada.')
            return redirect('reservas:mis_turnos')
    
    def _confirmar_wompi(self, request, reserva):
        """
        Confirma el pago con Wompi.
        """
        # Obtener el ID de la transacción de los parámetros
        transaction_id = request.GET.get('id')
        
        if not transaction_id:
            messages.error(request, 'No se recibió el ID de la transacción.')
            return redirect('reservas:mis_turnos')
        
        # Verificar el estado de la transacción
        medio_pago = reserva.medio_pago
        base_url = "https://sandbox.wompi.co/v1" if medio_pago.sandbox else "https://production.wompi.co/v1"
        
        try:
            # Consultar el estado de la transacción
            response = requests.get(f"{base_url}/transactions/{transaction_id}", headers={
                'Authorization': f'Bearer {medio_pago.api_key}'
            })
            
            if response.status_code == 200:
                data = response.json()
                
                if data['data']['status'] == 'APPROVED':
                    # Confirmar la reserva
                    reserva.confirmar()
                    messages.success(request, 'Pago confirmado y reserva confirmada exitosamente.')
                    return redirect('reservas:mis_turnos')
                else:
                    messages.error(request, f"El pago no fue aprobado. Estado: {data['data']['status']}")
            else:
                messages.error(request, 'Error al verificar el estado del pago.')
        except Exception as e:
            messages.error(request, f'Error al procesar la confirmación: {str(e)}')
        
        return redirect('reservas:mis_turnos')
    
    def _confirmar_payu(self, request, reserva):
        """
        Confirma el pago con PayU.
        """
        # Obtener el estado de la transacción de los parámetros
        state_pol = request.GET.get('state_pol')
        reference_sale = request.GET.get('reference_sale')
        
        if not state_pol or not reference_sale:
            messages.error(request, 'No se recibieron los parámetros necesarios.')
            return redirect('reservas:mis_turnos')
        
        # Verificar que la referencia coincida
        if reference_sale != reserva.referencia_pago:
            messages.error(request, 'La referencia de pago no coincide.')
            return redirect('reservas:mis_turnos')
        
        # Verificar el estado de la transacción
        if state_pol == '4':  # Aprobada
            # Confirmar la reserva
            reserva.confirmar()
            messages.success(request, 'Pago confirmado y reserva confirmada exitosamente.')
        else:
            messages.error(request, f"El pago no fue aprobado. Estado: {state_pol}")
        
        return redirect('reservas:mis_turnos')
    
    def _confirmar_nequi(self, request, reserva):
        """
        Confirma el pago con Nequi (simulación).
        """
        # Simular una confirmación exitosa
        # Confirmar la reserva
        reserva.confirmar()
        
        # Verificar si la bahía tiene cámara para generar QR
        tiene_camara = reserva.bahia.tiene_camara
        qr_url = None
        
        if tiene_camara and hasattr(reserva.bahia, 'ip_camara') and reserva.bahia.ip_camara:
            # Generar URL única para la transmisión si no existe
            if not reserva.stream_token:
                import uuid
                stream_token = f"{reserva.id}-{uuid.uuid4().hex[:8]}"
                reserva.stream_token = stream_token
                reserva.save(update_fields=['stream_token'])
            else:
                stream_token = reserva.stream_token
                
            stream_url = f"/stream/{stream_token}/"
            
            # Generar QR con la URL de transmisión
            import qrcode
            import io
            from django.conf import settings
            import os
            
            # URL completa para el QR (incluye dominio)
            qr_data = request.build_absolute_uri(stream_url)
            
            # Crear el código QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Crear imagen del QR
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Guardar la imagen en MEDIA_ROOT
            qr_filename = f"qr_reserva_{reserva.id}.png"
            qr_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', qr_filename)
            
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(qr_path), exist_ok=True)
            
            # Guardar la imagen
            img.save(qr_path)
            
            # URL para acceder a la imagen
            qr_url = f"{settings.MEDIA_URL}qr_codes/{qr_filename}"
        
        # Renderizar la plantilla de confirmación
        context = {
            'reserva': reserva,
            'qr_url': qr_url
        }
        
        return render(request, 'reservas/confirmacion_pago.html', context)
        
    def _confirmar_epayco(self, request, reserva):
        """
        Confirma el pago con ePayco.
        """
        # Obtener el estado de la transacción de los parámetros
        ref_payco = request.GET.get('ref_payco')
        
        if not ref_payco:
            messages.error(request, 'No se recibió la referencia de pago.')
            return redirect('reservas:mis_turnos')
        
        # Verificar el estado de la transacción
        medio_pago = reserva.medio_pago
        base_url = "https://secure.sandbox.epayco.co" if medio_pago.sandbox else "https://secure.epayco.co"
        
        try:
            # Consultar el estado de la transacción
            response = requests.get(f"{base_url}/validation/v1/reference/{ref_payco}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data['success'] and data['data']['x_response'] == 'Aceptada':
                    # Confirmar la reserva
                    reserva.confirmar()
                    messages.success(request, 'Pago confirmado y reserva confirmada exitosamente.')
                    return redirect('reservas:mis_turnos')
                else:
                    messages.error(request, f"El pago no fue aprobado. Estado: {data['data']['x_response']}")
            else:
                messages.error(request, 'Error al verificar el estado del pago.')
        except Exception as e:
            messages.error(request, f'Error al procesar la confirmación: {str(e)}')
        
        return redirect('reservas:mis_turnos')


@method_decorator(csrf_exempt, name='dispatch')
class WompiCallbackView(View):
    """
    Vista para recibir callbacks de Wompi.
    """
    def post(self, request, *args, **kwargs):
        try:
            # Obtener los datos del callback
            data = json.loads(request.body)
            
            # Verificar el evento
            if data['event'] != 'transaction.updated':
                return HttpResponse(status=200)
            
            # Obtener los datos de la transacción
            transaction = data['data']['transaction']
            reference = transaction['reference']
            status = transaction['status']
            
            # Buscar la reserva por la referencia
            try:
                reserva_id = reference.split('-')[1]
                reserva = Reserva.objects.get(id=reserva_id, referencia_pago=reference)
            except (IndexError, Reserva.DoesNotExist):
                return HttpResponse(status=200)
            
            # Verificar el estado de la transacción
            if status == 'APPROVED' and reserva.estado == Reserva.PENDIENTE:
                # Confirmar la reserva
                reserva.confirmar()
            
            return HttpResponse(status=200)
        except Exception as e:
            # Registrar el error pero responder con éxito para evitar reintentos
            print(f"Error en WompiCallbackView: {str(e)}")
            return HttpResponse(status=200)


@method_decorator(csrf_exempt, name='dispatch')
class PayUCallbackView(View):
    """
    Vista para recibir callbacks de PayU.
    """
    def post(self, request, *args, **kwargs):
        try:
            # Obtener los datos del callback
            reference_sale = request.POST.get('reference_sale')
            state_pol = request.POST.get('state_pol')
            sign = request.POST.get('sign')
            
            if not all([reference_sale, state_pol, sign]):
                return HttpResponse(status=200)
            
            # Buscar la reserva por la referencia
            try:
                reserva = Reserva.objects.get(referencia_pago=reference_sale)
            except Reserva.DoesNotExist:
                return HttpResponse(status=200)
            
            # Verificar la firma
            medio_pago = reserva.medio_pago
            api_key = medio_pago.api_secret
            
            # Construir la cadena para verificar la firma
            value = request.POST.get('value')
            currency = request.POST.get('currency')
            transaction_id = request.POST.get('transaction_id')
            
            signature_string = f"{api_key}~{medio_pago.merchant_id}~{reference_sale}~{value}~{currency}~{state_pol}"
            local_signature = hashlib.md5(signature_string.encode()).hexdigest()
            
            if local_signature != sign:
                return HttpResponse(status=200)
            
            # Verificar el estado de la transacción
            if state_pol == '4' and reserva.estado == Reserva.PENDIENTE:  # Aprobada
                # Confirmar la reserva
                reserva.confirmar()
            
            return HttpResponse(status=200)
        except Exception as e:
            # Registrar el error pero responder con éxito para evitar reintentos
            print(f"Error en PayUCallbackView: {str(e)}")
            return HttpResponse(status=200)


@method_decorator(csrf_exempt, name='dispatch')
class EpaycoCallbackView(View):
    """
    Vista para recibir callbacks de ePayco.
    """
    def post(self, request, *args, **kwargs):
        try:
            # Obtener los datos del callback
            x_ref_payco = request.POST.get('x_ref_payco')
            x_transaction_state = request.POST.get('x_transaction_state')
            x_signature = request.POST.get('x_signature')
            
            if not all([x_ref_payco, x_transaction_state, x_signature]):
                return HttpResponse(status=200)
            
            # Obtener la referencia interna
            x_extra1 = request.POST.get('x_extra1')  # Aquí se envía la referencia de la reserva
            
            if not x_extra1:
                return HttpResponse(status=200)
            
            # Buscar la reserva por la referencia
            try:
                reserva = Reserva.objects.get(referencia_pago=x_extra1)
            except Reserva.DoesNotExist:
                return HttpResponse(status=200)
            
            # Verificar la firma
            medio_pago = reserva.medio_pago
            p_cust_id = medio_pago.merchant_id
            p_key = medio_pago.api_secret
            
            x_amount = request.POST.get('x_amount')
            x_currency_code = request.POST.get('x_currency_code')
            
            signature_string = f"{p_cust_id}^{p_key}^{x_ref_payco}^{x_transaction_state}^{x_amount}^{x_currency_code}"
            local_signature = hashlib.sha256(signature_string.encode()).hexdigest()
            
            if local_signature != x_signature:
                return HttpResponse(status=200)
            
            # Verificar el estado de la transacción
            if x_transaction_state == '1' and reserva.estado == Reserva.PENDIENTE:  # Aceptada
                # Confirmar la reserva
                reserva.confirmar()
            
            return HttpResponse(status=200)
        except Exception as e:
            # Registrar el error pero responder con éxito para evitar reintentos
            print(f"Error en EpaycoCallbackView: {str(e)}")
            return HttpResponse(status=200)

class VerCamaraView(View):
    """Vista para ver la cámara web de una bahía usando token de acceso"""
    template_name = 'reservas/ver_camara.html'
    
    def get(self, request, token):
        # Obtener la reserva por el token de transmisión
        reserva = get_object_or_404(Reserva, stream_token=token)
        
        # Verificar que la reserva esté confirmada o en proceso
        if reserva.estado not in [Reserva.CONFIRMADA, Reserva.EN_PROCESO]:
            messages.error(request, 'Solo puedes ver la cámara de reservas confirmadas o en proceso.')
            return redirect('reservas:mis_turnos')
        
        # Verificar que la bahía tenga cámara y código QR
        bahia = reserva.bahia
        if not bahia or not bahia.tiene_camara or not bahia.ip_camara:
            messages.error(request, 'Esta bahía no tiene cámara configurada.')
            return redirect('reservas:mis_turnos')
        
        # Verificar que la fecha y hora actual esté dentro del rango de la reserva
        ahora = timezone.now()
        duracion_minutos = reserva.servicio.duracion_minutos
        fin_servicio = reserva.fecha_hora + timezone.timedelta(minutes=duracion_minutos)
        
        # Permitir ver la cámara 15 minutos antes y 15 minutos después del servicio
        inicio_permitido = reserva.fecha_hora - timezone.timedelta(minutes=15)
        fin_permitido = fin_servicio + timezone.timedelta(minutes=15)
        
        if ahora < inicio_permitido or ahora > fin_permitido:
            messages.error(request, 'La cámara solo está disponible 15 minutos antes, durante y hasta 15 minutos después de tu reserva.')
            return redirect('reservas:mis_turnos')
        
        # Obtener el vehículo asociado a la reserva si existe
        vehiculo = None
        try:
            vehiculo = Vehiculo.objects.filter(cliente=reserva.cliente).first()
        except:
            pass
        
        context = {
            'reserva': reserva,
            'bahia': bahia,
            'vehiculo': vehiculo
        }
        
        return render(request, self.template_name, context)

# Vistas basadas en clases para plantillas HTML
class ReservarTurnoView(LoginRequiredMixin, TemplateView):
    template_name = 'reservas/reservar_turno.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['servicios'] = Servicio.objects.filter(activo=True)
        context['vehiculos'] = Vehiculo.objects.filter(cliente=self.request.user.cliente)
        # Solo enviar el medio de pago Nequi que está en la base de datos
        context['medios_pago'] = MedioPago.objects.filter(activo=True, tipo=MedioPago.NEQUI)
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            # Obtener datos del formulario
            servicio_id = request.POST.get('servicio')
            fecha_str = request.POST.get('fecha')
            hora_str = request.POST.get('hora')
            vehiculo_id = request.POST.get('vehiculo')
            bahia_id = request.POST.get('bahia_id')
            medio_pago_id = request.POST.get('medio_pago')
            notas = request.POST.get('notas', '')
            
            # Verificar si es una solicitud AJAX
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            # Validar datos
            if not all([servicio_id, fecha_str, hora_str, vehiculo_id, bahia_id, medio_pago_id]):
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'Por favor complete todos los campos requeridos.'})
                messages.error(request, 'Por favor complete todos los campos requeridos.')
                return redirect('reservas:reservar_turno')
            
            # Obtener objetos
            servicio = get_object_or_404(Servicio, id=servicio_id)
            
            # Manejar el caso de un nuevo vehículo
            if vehiculo_id == 'nuevo':
                # Crear un nuevo vehículo con los datos del formulario
                vehiculo = Vehiculo.objects.create(
                    cliente=request.user.cliente,
                    marca=request.POST.get('marca'),
                    modelo=request.POST.get('modelo'),
                    anio=request.POST.get('anio'),
                    placa=request.POST.get('placa'),
                    tipo=request.POST.get('tipo_vehiculo'),
                    color=request.POST.get('color')
                )
            else:
                # Obtener el vehículo existente
                vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id, cliente=request.user.cliente)
                
            bahia = get_object_or_404(Bahia, id=bahia_id, activo=True)
            medio_pago = get_object_or_404(MedioPago, id=medio_pago_id, activo=True)
            
            # Convertir fecha y hora
            fecha_hora = datetime.strptime(f'{fecha_str} {hora_str}', '%Y-%m-%d %H:%M')
            fecha_hora = timezone.make_aware(fecha_hora)
            
            # Verificar que la fecha no sea en el pasado
            if fecha_hora < timezone.now():
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'No se pueden hacer reservas para fechas pasadas.'})
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
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'El horario seleccionado no está disponible.'})
                messages.error(request, 'El horario seleccionado no está disponible.')
                return redirect('reservas:reservar_turno')
            
            # Buscar una bahía disponible
            # Primero obtenemos todas las bahías activas
            bahias_activas = Bahia.objects.filter(activo=True)
            
            # Luego obtenemos las bahías que ya están ocupadas en ese horario
            bahias_ocupadas = Reserva.objects.filter(
                fecha_hora=fecha_hora,
                estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
            ).values_list('bahia', flat=True)
            
            # Filtramos las bahías disponibles
            bahias_disponibles = bahias_activas.exclude(id__in=bahias_ocupadas)
            
            if not bahias_disponibles.exists():
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'No hay bahías disponibles para el horario seleccionado.'})
                messages.error(request, 'No hay bahías disponibles para el horario seleccionado.')
                return redirect('reservas:reservar_turno')
            
            # Seleccionamos la primera bahía disponible
            bahia_seleccionada = bahias_disponibles.first()
            
            # Crear la reserva
            reserva = Reserva.objects.create(
                cliente=request.user.cliente,
                servicio=servicio,
                fecha_hora=fecha_hora,
                bahia=bahia,
                notas=notas,
                estado=Reserva.PENDIENTE,
                medio_pago=medio_pago
            )
            
            # Si el medio de pago es una pasarela, redirigir al proceso de pago
            if medio_pago.es_pasarela():
                return redirect('reservas:procesar_pago', reserva_id=reserva.id)
            
            # Incrementar contador de reservas en el horario
            horario.incrementar_reservas()
            
            # Verificar si la bahía tiene cámara para generar QR
            tiene_camara = bahia.tiene_camara
            qr_url = None
            qr_pago_url = None
            
            if tiene_camara and bahia.ip_camara:
                # Generar URL única para la transmisión
                import uuid
                stream_token = f"{reserva.id}-{uuid.uuid4().hex[:8]}"
                stream_url = f"/stream/{stream_token}/"
                
                # Guardar el token en la reserva si existe el campo
                if hasattr(reserva, 'stream_token'):
                    reserva.stream_token = stream_token
                    reserva.save(update_fields=['stream_token'])
                
                # Generar QR con la URL de transmisión
                import qrcode
                import io
                from django.conf import settings
                import os
                
                # URL completa para el QR (incluye dominio)
                qr_data = request.build_absolute_uri(stream_url)
                
                # Crear el código QR
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_data)
                qr.make(fit=True)
                
                # Crear imagen del QR
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Guardar la imagen en MEDIA_ROOT
                qr_filename = f"qr_reserva_{reserva.id}.png"
                qr_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', qr_filename)
                
                # Asegurar que el directorio existe
                os.makedirs(os.path.dirname(qr_path), exist_ok=True)
                
                # Guardar la imagen
                img.save(qr_path)
                
                # URL para acceder a la imagen
                qr_url = f"{settings.MEDIA_URL}qr_codes/{qr_filename}"
            
            # Generar QR o enlace para el pago con Nequi si corresponde
            if medio_pago.tipo == MedioPago.NEQUI:
                # Generar QR para el pago con Nequi
                import qrcode
                import os
                from django.conf import settings
                
                # Datos para el QR de pago (simulación)
                monto = servicio.precio
                referencia = f"RESERVA-{reserva.id}-{uuid.uuid4().hex[:8]}"
                
                # Guardar la referencia en la reserva para validar el callback
                reserva.referencia_pago = referencia
                reserva.save(update_fields=['referencia_pago'])
                
                # URL para el pago con Nequi (simulación)
                pago_url = request.build_absolute_uri(reverse('reservas:procesar_pago', args=[reserva.id]))
                
                # Crear el código QR para el pago
                qr_pago = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr_pago.add_data(pago_url)
                qr_pago.make(fit=True)
                
                # Crear imagen del QR de pago
                img_pago = qr_pago.make_image(fill_color="black", back_color="white")
                
                # Guardar la imagen en MEDIA_ROOT
                qr_pago_filename = f"qr_pago_{reserva.id}.png"
                qr_pago_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', qr_pago_filename)
                
                # Asegurar que el directorio existe
                os.makedirs(os.path.dirname(qr_pago_path), exist_ok=True)
                
                # Guardar la imagen
                img_pago.save(qr_pago_path)
                
                # URL para acceder a la imagen del QR de pago
                qr_pago_url = f"{settings.MEDIA_URL}qr_codes/{qr_pago_filename}"
            
            # Crear notificación
            Notificacion.objects.create(
                cliente=request.user.cliente,
                tipo=Notificacion.RESERVA_CREADA,
                titulo='Reserva Creada',
                mensaje=f'Tu reserva para el servicio {servicio.nombre} ha sido creada para el {fecha_hora.strftime("%d/%m/%Y a las %H:%M")}. Recibirás una confirmación pronto.',
            )
            
            if is_ajax:
                return JsonResponse({
                    'success': True, 
                    'tiene_camara': tiene_camara,
                    'qr_url': qr_url,
                    'qr_pago_url': qr_pago_url,
                    'tiene_qr_pago': qr_pago_url is not None,
                    'medio_pago': medio_pago.get_tipo_display(),
                    'reserva_id': reserva.id
                })
            
            messages.success(request, 'Reserva creada exitosamente. Recibirás una confirmación pronto.')
            return redirect('reservas:mis_turnos')
            
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            if 'is_ajax' in locals() and is_ajax:
                return JsonResponse({'success': False, 'error': f'Error al crear la reserva: {str(e)}'})
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
        
        # Guardar la bahía antes de cancelar para poder liberarla
        bahia = reserva.bahia
        
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


class ObtenerMediosPagoView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            medios_pago = MedioPago.objects.filter(activo=True)
            data = [{
                'id': mp.id,
                'nombre': mp.nombre,
                'tipo': mp.get_tipo_display(),
                'descripcion': mp.descripcion,
                'es_pasarela': mp.es_pasarela()
            } for mp in medios_pago]
            
            return JsonResponse({'medios_pago': data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


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
            # Guardar la duración del servicio para calcular disponibilidad
            duracion_servicio = servicio.duracion_minutos
            
            # Verificar si hay bahías activas disponibles
            bahias_activas = Bahia.objects.filter(activo=True).count()
            if bahias_activas == 0:
                return JsonResponse({'error': 'No hay bahías disponibles en el sistema'}, status=400)
            
            # Obtener horarios disponibles para esa fecha
            horarios_disponibles = HorarioDisponible.objects.filter(
                fecha=fecha,
                disponible=True
            ).order_by('hora_inicio')
            
            # Filtrar horarios que están llenos (esta_lleno es una propiedad calculada, no un campo)
            # Nota: No podemos usar exclude(esta_lleno=True) porque es una propiedad calculada
            horarios_filtrados = []
            for h in horarios_disponibles:
                if h.reservas_actuales < h.capacidad:  # Verificación directa en lugar de usar la propiedad
                    horarios_filtrados.append(h)
            horarios_disponibles = horarios_filtrados
            
            # Si no hay horarios específicos para esa fecha, usar la disponibilidad general
            if not horarios_disponibles:
                # Obtener el día de la semana (0-6, donde 0 es lunes)
                dia_semana = fecha.weekday()
                
                # Buscar disponibilidad general para ese día
                disponibilidad_general = DisponibilidadHoraria.objects.filter(
                    dia_semana=dia_semana,
                    activo=True
                ).order_by('hora_inicio')
                
                # Crear horarios disponibles basados en la disponibilidad general y la duración del servicio
                horarios = []
                for disp in disponibilidad_general:
                    # Crear intervalos exactos según la duración del servicio seleccionado
                    # Empezamos desde la hora de inicio del día
                    hora_actual = disp.hora_inicio
                    
                    # Generamos horarios en intervalos de 30 minutos para mostrar más opciones
                    # Usamos un intervalo fijo de 30 minutos para mostrar más opciones
                    intervalo_minutos = 30
                    
                    while hora_actual < disp.hora_fin:
                        # Calculamos la hora de fin del servicio
                        hora_fin = (datetime.combine(fecha, hora_actual) + timedelta(minutes=duracion_servicio)).time()
                        
                        # Solo agregamos el horario si el servicio cabe completamente en el horario disponible
                        if hora_fin <= disp.hora_fin:
                            # Verificamos disponibilidad de bahías para este horario
                            hora_inicio_dt = timezone.make_aware(datetime.combine(fecha, hora_actual))
                            hora_fin_dt = timezone.make_aware(datetime.combine(fecha, hora_fin))
                            
                            # Obtenemos todas las bahías activas
                            bahias_activas = Bahia.objects.filter(activo=True)
                            
                            # Obtenemos las reservas que se solapan con este horario considerando la duración del servicio
                            reservas_solapadas = Reserva.objects.filter(
                                fecha_hora__lt=hora_fin_dt,
                                fecha_hora__gte=hora_inicio_dt,
                                estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
                            )
                            
                            # También considerar reservas que empezaron antes pero terminan durante nuestro horario
                            otras_reservas = Reserva.objects.filter(
                                fecha_hora__lt=hora_inicio_dt,
                                estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
                            )
                            
                            # Filtrar aquellas que se solapan con nuestro horario
                            for reserva in otras_reservas:
                                # Calcular la hora de fin de la reserva según la duración del servicio
                                fin_reserva = reserva.fecha_hora + timedelta(minutes=reserva.servicio.duracion_minutos)
                                # Si la reserva termina después de nuestra hora de inicio, hay solapamiento
                                if fin_reserva > hora_inicio_dt:
                                    reservas_solapadas = reservas_solapadas | Reserva.objects.filter(id=reserva.id)
                            
                            # Obtener las bahías ocupadas
                            bahias_ocupadas = reservas_solapadas.values_list('bahia', flat=True).distinct()
                            
                            # Calcular bahías disponibles
                            bahias_disponibles = bahias_activas.exclude(id__in=bahias_ocupadas).count()
                            
                            # Solo agregamos el horario si hay bahías disponibles
                            if bahias_disponibles > 0:
                                horarios.append({
                                    'hora_inicio': hora_actual.strftime('%H:%M'),
                                    'hora_fin': hora_fin.strftime('%H:%M'),
                                    'disponible': True,
                                    'bahias_disponibles': bahias_disponibles
                                })
                        
                        # Avanzamos en intervalos de 30 minutos para mostrar más opciones
                        hora_actual = (datetime.combine(fecha, hora_actual) + timedelta(minutes=intervalo_minutos)).time()
                
                # Ya no necesitamos filtrar horarios aquí, ya que lo hacemos al crearlos
                # Los horarios ya incluyen solo aquellos donde hay bahías disponibles
            else:
                # Usar los horarios específicos de la fecha, considerando la duración del servicio
                horarios = []
                for h in horarios_disponibles:
                    # Para cada horario, verificar si hay bahías disponibles y si el servicio cabe en el horario
                    hora_inicio = datetime.combine(fecha, h.hora_inicio)
                    # Calcular hora fin según la duración del servicio
                    hora_fin_servicio = hora_inicio + timedelta(minutes=duracion_servicio)
                    hora_fin = datetime.combine(fecha, h.hora_fin)
                    
                    # Verificar que el servicio quepa en el horario disponible
                    if hora_fin_servicio.time() > h.hora_fin:
                        continue  # El servicio no cabe en este horario, saltamos
                    
                    # Obtener todas las bahías activas
                    bahias_activas = Bahia.objects.filter(activo=True)
                    
                    # Obtener las reservas que se solapan con este horario considerando la duración del servicio
                    reservas_solapadas = Reserva.objects.filter(
                        fecha_hora__lt=timezone.make_aware(hora_fin_servicio),
                        fecha_hora__gte=timezone.make_aware(hora_inicio),
                        estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
                    )
                    
                    # También considerar reservas que empezaron antes pero terminan durante nuestro horario
                    # Obtener todas las reservas activas que podrían solaparse
                    otras_reservas = Reserva.objects.filter(
                        fecha_hora__lt=timezone.make_aware(hora_inicio),
                        estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
                    )
                    
                    # Filtrar aquellas que se solapan con nuestro horario
                    for reserva in otras_reservas:
                        # Calcular la hora de fin de la reserva según la duración del servicio
                        fin_reserva = reserva.fecha_hora + timedelta(minutes=reserva.servicio.duracion_minutos)
                        # Si la reserva termina después de nuestra hora de inicio, hay solapamiento
                        if fin_reserva > timezone.make_aware(hora_inicio):
                            reservas_solapadas = reservas_solapadas | Reserva.objects.filter(id=reserva.id)
                    
                    # Obtener las bahías ocupadas
                    bahias_ocupadas = reservas_solapadas.values_list('bahia', flat=True).distinct()
                    
                    # Calcular bahías disponibles
                    bahias_disponibles = bahias_activas.exclude(id__in=bahias_ocupadas).count()
                    
                    # Solo agregar el horario si hay bahías disponibles
                    if bahias_disponibles > 0:
                        # Crear intervalos de 30 minutos dentro del horario disponible
                        hora_actual = h.hora_inicio
                        intervalo_minutos = 30
                        
                        while hora_actual <= (datetime.combine(fecha, h.hora_fin) - timedelta(minutes=duracion_servicio)).time():
                            hora_fin_intervalo = (datetime.combine(fecha, hora_actual) + timedelta(minutes=duracion_servicio)).time()
                            
                            # Verificar disponibilidad específica para este intervalo
                            hora_inicio_dt = timezone.make_aware(datetime.combine(fecha, hora_actual))
                            hora_fin_dt = timezone.make_aware(datetime.combine(fecha, hora_fin_intervalo))
                            
                            # Verificar reservas solapadas para este intervalo específico
                            reservas_intervalo = Reserva.objects.filter(
                                fecha_hora__lt=hora_fin_dt,
                                fecha_hora__gte=hora_inicio_dt,
                                estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
                            ).count()
                            
                            # Si hay menos reservas que bahías, hay disponibilidad
                            bahias_disponibles_intervalo = bahias_activas.count() - reservas_intervalo
                            
                            if bahias_disponibles_intervalo > 0:
                                horarios.append({
                                    'hora_inicio': hora_actual.strftime('%H:%M'),
                                    'hora_fin': hora_fin_intervalo.strftime('%H:%M'),
                                    'disponible': True,
                                    'bahias_disponibles': bahias_disponibles_intervalo
                                })
                            
                            # Avanzar al siguiente intervalo
                            hora_actual = (datetime.combine(fecha, hora_actual) + timedelta(minutes=intervalo_minutos)).time()
            
            return JsonResponse({'horarios': horarios})
            
        except Exception as e:
            import traceback
            print(f"Error al cargar horarios disponibles: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': 'Error al cargar los horarios disponibles. Por favor, inténtalo de nuevo.'}, status=500)

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
    
    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """Completar una reserva"""
        reserva = self.get_object()
        
        # Verificar si la reserva puede ser completada
        if reserva.estado != Reserva.EN_PROCESO:
            return Response({
                'error': 'Solo se pueden completar reservas en proceso'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Completar la reserva usando el método del modelo que elimina el código QR
        if reserva.completar_servicio():
            # Crear notificación
            Notificacion.objects.create(
                cliente=reserva.cliente,
                tipo=Notificacion.SERVICIO_FINALIZADO,
                titulo='Servicio Completado',
                mensaje=f'Tu servicio {reserva.servicio.nombre} ha sido completado. ¡Gracias por confiar en nosotros!',
            )
            return Response({
                'mensaje': 'Reserva completada exitosamente'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'No se pudo completar la reserva'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_serializer_class(self):
        """Seleccionar el serializer según la acción"""
        if self.action in ['update', 'partial_update']:
            return ReservaUpdateSerializer
        return ReservaSerializer
    
    def perform_create(self, serializer):
        """Crear una reserva y asignar automáticamente una bahía disponible"""
        # Obtener fecha y hora de la reserva
        fecha_hora = serializer.validated_data.get('fecha_hora')
        
        # Buscar una bahía disponible
        # Primero obtenemos todas las bahías activas
        bahias_activas = Bahia.objects.filter(activo=True)
        
        if not bahias_activas.exists():
            raise serializers.ValidationError({'error': 'No hay bahías disponibles en el sistema.'})
        
        # Luego obtenemos las bahías que ya están ocupadas en ese horario
        bahias_ocupadas = Reserva.objects.filter(
            fecha_hora=fecha_hora,
            estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
        ).values_list('bahia', flat=True)
        
        # Filtramos las bahías disponibles
        bahias_disponibles = bahias_activas.exclude(id__in=bahias_ocupadas)
        
        if not bahias_disponibles.exists():
            raise serializers.ValidationError({'error': 'No hay bahías disponibles para el horario seleccionado.'})
        
        # Seleccionamos la primera bahía disponible
        bahia_seleccionada = bahias_disponibles.first()
        
        # Guardar la reserva con la bahía asignada
        reserva = serializer.save(bahia=bahia_seleccionada)
        
        # Crear notificación para el cliente
        Notificacion.objects.create(
            cliente=reserva.cliente,
            tipo=Notificacion.RESERVA_CREADA,
            titulo='Reserva Creada',
            mensaje=f'Tu reserva para el servicio {reserva.servicio.nombre} ha sido creada exitosamente para el {reserva.fecha_hora.strftime("%d/%m/%Y a las %H:%M")}.',
        )
    
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


class ObtenerBahiasDisponiblesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            fecha_str = request.GET.get('fecha')
            hora_str = request.GET.get('hora')
            servicio_id = request.GET.get('servicio_id')
            
            if not all([fecha_str, hora_str, servicio_id]):
                return JsonResponse({'error': 'Se requieren fecha, hora y servicio_id'}, status=400)
            
            # Convertir fecha y hora
            try:
                fecha_hora = datetime.strptime(f'{fecha_str} {hora_str}', '%Y-%m-%d %H:%M')
                fecha_hora = timezone.make_aware(fecha_hora)
            except ValueError:
                return JsonResponse({'error': 'Formato de fecha u hora inválido'}, status=400)
            
            # Verificar que la fecha no sea en el pasado
            if fecha_hora < timezone.now():
                return JsonResponse({'error': 'No se pueden consultar bahías para fechas pasadas'}, status=400)
            
            # Obtener servicio y su duración
            servicio = get_object_or_404(Servicio, id=servicio_id)
            duracion_servicio = servicio.duracion_minutos
            
            # Calcular hora de fin del servicio
            hora_fin = fecha_hora + timedelta(minutes=duracion_servicio)
            
            # Obtener todas las bahías activas
            bahias_activas = Bahia.objects.filter(activo=True)
            
            # Obtener las reservas que se solapan con este horario
            reservas_solapadas = Reserva.objects.filter(
                fecha_hora__lt=hora_fin,
                fecha_hora__gte=fecha_hora,
                estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
            )
            
            # También considerar reservas que empezaron antes pero terminan durante nuestro horario
            otras_reservas = Reserva.objects.filter(
                fecha_hora__lt=fecha_hora,
                estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
            )
            
            # Filtrar aquellas que se solapan con nuestro horario
            for reserva in otras_reservas:
                fin_reserva = reserva.fecha_hora + timedelta(minutes=reserva.servicio.duracion_minutos)
                if fin_reserva > fecha_hora:
                    reservas_solapadas = reservas_solapadas | Reserva.objects.filter(id=reserva.id)
            
            # Obtener las bahías ocupadas
            bahias_ocupadas = reservas_solapadas.values_list('bahia', flat=True).distinct()
            
            # Filtrar las bahías disponibles
            bahias_disponibles = bahias_activas.exclude(id__in=bahias_ocupadas)
            
            # Preparar respuesta
            bahias_data = [{
                'id': bahia.id,
                'nombre': bahia.nombre,
                'descripcion': bahia.descripcion,
                'tiene_camara': bahia.tiene_camara
            } for bahia in bahias_disponibles]
            
            return JsonResponse({
                'fecha_hora': fecha_hora.strftime('%Y-%m-%d %H:%M'),
                'servicio': servicio.nombre,
                'duracion_minutos': duracion_servicio,
                'bahias_disponibles': bahias_data,
                'total_disponibles': bahias_disponibles.count()
            })
            
        except Exception as e:
            import traceback
            print(f"Error al obtener bahías disponibles: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': 'Error al obtener las bahías disponibles. Por favor, inténtalo de nuevo.'}, status=500)


class BahiaViewSet(viewsets.ModelViewSet):
    """ViewSet para el modelo Bahia"""
    queryset = Bahia.objects.all()
    serializer_class = BahiaSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'descripcion']
    
    def get_permissions(self):
        """Definir permisos según la acción"""
        if self.action in ['ver_camara', 'bahias_disponibles']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def ver_camara(self, request, pk=None):
        """Endpoint para ver la cámara de una bahía específica"""
        bahia = self.get_object()
        if not bahia.tiene_camara or not bahia.ip_camara:
            return Response({'error': 'Esta bahía no tiene cámara configurada'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'bahia': bahia.nombre,
            'ip_camara': bahia.ip_camara,
            'codigo_qr_url': request.build_absolute_uri(bahia.codigo_qr.url) if bahia.codigo_qr else None
        })
        
    @action(detail=False, methods=['get'])
    def bahias_disponibles(self, request):
        """Endpoint para obtener bahías disponibles en una fecha y hora específica"""
        try:
            fecha_str = request.query_params.get('fecha')
            hora_str = request.query_params.get('hora')
            servicio_id = request.query_params.get('servicio_id')
            
            if not all([fecha_str, hora_str, servicio_id]):
                return Response({'error': 'Se requieren fecha, hora y servicio_id'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Convertir fecha y hora
            try:
                fecha_hora = datetime.strptime(f'{fecha_str} {hora_str}', '%Y-%m-%d %H:%M')
                fecha_hora = timezone.make_aware(fecha_hora)
            except ValueError:
                return Response({'error': 'Formato de fecha u hora inválido'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar que la fecha no sea en el pasado
            if fecha_hora < timezone.now():
                return Response({'error': 'No se pueden consultar bahías para fechas pasadas'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener servicio y su duración
            servicio = get_object_or_404(Servicio, id=servicio_id)
            duracion_servicio = servicio.duracion_minutos
            
            # Calcular hora de fin del servicio
            hora_fin = fecha_hora + timedelta(minutes=duracion_servicio)
            
            # Obtener todas las bahías activas
            bahias_activas = Bahia.objects.filter(activo=True)
            
            # Obtener las reservas que se solapan con este horario
            reservas_solapadas = Reserva.objects.filter(
                fecha_hora__lt=hora_fin,
                fecha_hora__gte=fecha_hora,
                estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
            )
            
            # También considerar reservas que empezaron antes pero terminan durante nuestro horario
            otras_reservas = Reserva.objects.filter(
                fecha_hora__lt=fecha_hora,
                estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
            )
            
            # Filtrar aquellas que se solapan con nuestro horario
            for reserva in otras_reservas:
                fin_reserva = reserva.fecha_hora + timedelta(minutes=reserva.servicio.duracion_minutos)
                if fin_reserva > fecha_hora:
                    reservas_solapadas = reservas_solapadas | Reserva.objects.filter(id=reserva.id)
            
            # Obtener las bahías ocupadas
            bahias_ocupadas = reservas_solapadas.values_list('bahia', flat=True).distinct()
            
            # Filtrar las bahías disponibles
            bahias_disponibles = bahias_activas.exclude(id__in=bahias_ocupadas)
            
            # Serializar las bahías disponibles
            serializer = self.get_serializer(bahias_disponibles, many=True)
            
            return Response({
                'fecha_hora': fecha_hora.strftime('%Y-%m-%d %H:%M'),
                'servicio': servicio.nombre,
                'duracion_minutos': duracion_servicio,
                'bahias_disponibles': serializer.data,
                'total_disponibles': bahias_disponibles.count()
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def perform_update(self, serializer):
        """Sobrescribir el método perform_update para manejar la generación del código QR"""
        # Verificar si se está actualizando el campo tiene_camara o ip_camara
        instance = self.get_object()
        tiene_camara = serializer.validated_data.get('tiene_camara', instance.tiene_camara)
        ip_camara = serializer.validated_data.get('ip_camara', instance.ip_camara)
        
        # Si se desactiva la cámara, eliminar el código QR
        if not tiene_camara and instance.codigo_qr:
            instance.codigo_qr.delete(save=False)
            serializer.validated_data['codigo_qr'] = None
        
        # Guardar los cambios
        serializer.save()
    
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
        # Obtener fecha y hora de la reserva
        fecha_hora = serializer.validated_data.get('fecha_hora')
        
        # Buscar una bahía disponible
        # Primero obtenemos todas las bahías activas
        bahias_activas = Bahia.objects.filter(activo=True)
        
        # Luego obtenemos las bahías que ya están ocupadas en ese horario
        bahias_ocupadas = Reserva.objects.filter(
            fecha_hora=fecha_hora,
            estado__in=[Reserva.PENDIENTE, Reserva.CONFIRMADA, Reserva.EN_PROCESO]
        ).values_list('bahia', flat=True)
        
        # Filtramos las bahías disponibles
        bahias_disponibles = bahias_activas.exclude(id__in=bahias_ocupadas)
        
        if not bahias_disponibles.exists():
            raise serializers.ValidationError({'error': 'No hay bahías disponibles para el horario seleccionado.'})
        
        # Seleccionamos la primera bahía disponible
        bahia_seleccionada = bahias_disponibles.first()
        
        # Guardar la reserva con la bahía asignada
        reserva = serializer.save(bahia=bahia_seleccionada)
        
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
                
                # Liberar la bahía al completar el servicio
                # La bahía queda disponible para otras reservas
                
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
        
        # Confirmar la reserva usando el método del modelo que genera el código QR
        if reserva.confirmar():
            # Crear notificación
            Notificacion.objects.create(
                cliente=reserva.cliente,
                tipo=Notificacion.RESERVA_CONFIRMADA,
                titulo='Reserva Confirmada',
                mensaje=f'Tu reserva para el servicio {reserva.servicio.nombre} ha sido confirmada para el {reserva.fecha_hora.strftime("%d/%m/%Y a las %H:%M")}. ¡Te esperamos!',
            )
            
            # Si la bahía tiene cámara, incluir información sobre el código QR
            if reserva.bahia and reserva.bahia.tiene_camara and reserva.bahia.codigo_qr:
                Notificacion.objects.create(
                    cliente=reserva.cliente,
                    tipo=Notificacion.INFORMACION,
                    titulo='Cámara Web Disponible',
                    mensaje=f'Tu servicio cuenta con cámara web. Podrás ver el lavado de tu vehículo en vivo durante el horario de tu reserva.',
                )
        else:
            return Response({
                'error': 'No se pudo confirmar la reserva'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'mensaje': 'Reserva confirmada exitosamente'
        }, status=status.HTTP_200_OK)
