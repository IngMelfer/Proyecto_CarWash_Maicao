"""
Vistas específicas para manejar callbacks y webhooks de Nequi.
"""

import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from .models import Reserva, MedioPago
from .nequi_service import nequi_service
from clientes.models import Cliente

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class NequiCallbackView(View):
    """
    Vista para manejar el callback/webhook de Nequi cuando se confirma o rechaza un pago.
    """
    
    def post(self, request, *args, **kwargs):
        """
        Procesa la notificación webhook de Nequi.
        """
        try:
            # Obtener el cuerpo de la petición
            body = request.body.decode('utf-8')
            webhook_data = json.loads(body)
            
            logger.info(f"Webhook Nequi recibido: {webhook_data}")
            
            # Validar la firma del webhook (si está configurada)
            signature = request.headers.get('X-Nequi-Signature', '')
            if not nequi_service.validate_webhook_signature(body, signature):
                logger.warning("Firma de webhook Nequi inválida")
                return JsonResponse({'error': 'Firma inválida'}, status=400)
            
            # Procesar la notificación
            resultado = nequi_service.process_webhook_notification(webhook_data)
            
            if resultado['success']:
                transaction_id = resultado['transaction_id']
                status = resultado['status']
                
                # Buscar la reserva por referencia
                try:
                    reserva = Reserva.objects.get(referencia_pago=transaction_id)
                except Reserva.DoesNotExist:
                    logger.error(f"No se encontró reserva con referencia: {transaction_id}")
                    return JsonResponse({'error': 'Reserva no encontrada'}, status=404)
                
                # Procesar según el estado del pago
                if status == 'APPROVED' or status == 'SUCCESS':
                    self._confirmar_pago_exitoso(reserva, resultado)
                elif status == 'REJECTED' or status == 'FAILED':
                    self._rechazar_pago(reserva, resultado)
                elif status == 'PENDING':
                    self._pago_pendiente(reserva, resultado)
                
                return JsonResponse({'status': 'ok', 'message': 'Webhook procesado'})
            else:
                logger.error(f"Error al procesar webhook: {resultado.get('error')}")
                return JsonResponse({'error': 'Error al procesar webhook'}, status=500)
                
        except json.JSONDecodeError:
            logger.error("Error al decodificar JSON del webhook")
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            logger.error(f"Error inesperado en webhook: {str(e)}")
            return JsonResponse({'error': 'Error interno'}, status=500)
    
    def get(self, request, *args, **kwargs):
        """
        Maneja las peticiones GET (para verificación de webhook).
        """
        return JsonResponse({'status': 'ok', 'message': 'Webhook Nequi activo'})
    
    def _confirmar_pago_exitoso(self, reserva, resultado_webhook):
        """
        Confirma el pago exitoso y actualiza la reserva.
        """
        try:
            # Aplicar puntos si corresponde
            if hasattr(reserva, 'puntos_redimidos') and reserva.puntos_redimidos > 0:
                cliente = reserva.cliente
                if cliente.puntos >= reserva.puntos_redimidos:
                    cliente.puntos -= reserva.puntos_redimidos
                    cliente.save()
            
            # Confirmar la reserva
            reserva.estado = Reserva.CONFIRMADA
            reserva.fecha_confirmacion = resultado_webhook['processed_at']
            reserva.save()
            
            # Generar QR si el lavadero tiene cámara
            if hasattr(reserva.lavadero, 'tiene_camara') and reserva.lavadero.tiene_camara:
                from .utils import generar_qr_streaming
                qr_data = generar_qr_streaming(reserva)
                reserva.qr_streaming = qr_data
                reserva.save()
            
            logger.info(f"Pago Nequi confirmado para reserva {reserva.id}")
            
        except Exception as e:
            logger.error(f"Error al confirmar pago Nequi: {str(e)}")
    
    def _rechazar_pago(self, reserva, resultado_webhook):
        """
        Maneja el rechazo del pago.
        """
        try:
            reserva.estado = Reserva.CANCELADA
            reserva.save()
            
            logger.info(f"Pago Nequi rechazado para reserva {reserva.id}")
            
        except Exception as e:
            logger.error(f"Error al rechazar pago Nequi: {str(e)}")
    
    def _pago_pendiente(self, reserva, resultado_webhook):
        """
        Maneja el estado pendiente del pago.
        """
        try:
            # Mantener el estado actual de la reserva
            logger.info(f"Pago Nequi pendiente para reserva {reserva.id}")
            
        except Exception as e:
            logger.error(f"Error al procesar pago pendiente Nequi: {str(e)}")


class NequiStatusView(View):
    """
    Vista para consultar el estado de un pago Nequi desde el frontend.
    """
    
    def get(self, request, *args, **kwargs):
        """
        Consulta el estado de un pago Nequi.
        """
        transaction_id = request.GET.get('transaction_id')
        
        if not transaction_id:
            return JsonResponse({'error': 'ID de transacción requerido'}, status=400)
        
        try:
            # Consultar estado en Nequi
            resultado = nequi_service.check_payment_status(transaction_id)
            
            if resultado['success']:
                status = resultado['status']
                
                # Buscar la reserva
                try:
                    reserva = Reserva.objects.get(referencia_pago=transaction_id)
                    
                    return JsonResponse({
                        'success': True,
                        'status': status,
                        'reserva_id': reserva.id,
                        'reserva_estado': reserva.estado,
                        'data': resultado['data']
                    })
                except Reserva.DoesNotExist:
                    return JsonResponse({
                        'success': True,
                        'status': status,
                        'reserva_id': None,
                        'data': resultado['data']
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'error': resultado.get('error', 'Error al consultar estado')
                }, status=500)
                
        except Exception as e:
            logger.error(f"Error al consultar estado Nequi: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Error interno'
            }, status=500)


class NequiReturnView(View):
    """
    Vista para manejar el retorno desde la aplicación Nequi (si aplica).
    """
    
    def get(self, request, *args, **kwargs):
        """
        Maneja el retorno desde Nequi después del pago.
        """
        transaction_id = request.GET.get('transaction_id')
        status = request.GET.get('status', 'unknown')
        
        if transaction_id:
            try:
                reserva = Reserva.objects.get(referencia_pago=transaction_id)
                
                if status in ['approved', 'success']:
                    messages.success(request, 'Pago procesado exitosamente con Nequi.')
                    return redirect('reservas:confirmar_pago', reserva_id=reserva.id)
                elif status in ['rejected', 'failed']:
                    messages.error(request, 'El pago fue rechazado. Por favor, intenta nuevamente.')
                    return redirect('reservas:reservar_turno')
                else:
                    messages.info(request, 'El pago está siendo procesado. Te notificaremos cuando se confirme.')
                    return redirect('reservas:mis_reservas')
                    
            except Reserva.DoesNotExist:
                messages.error(request, 'No se encontró la reserva asociada.')
                return redirect('reservas:reservar_turno')
        
        messages.error(request, 'Información de pago incompleta.')
        return redirect('reservas:reservar_turno')