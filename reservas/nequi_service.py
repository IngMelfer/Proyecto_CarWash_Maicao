"""
Servicio de integración con la API de Nequi para procesar pagos push.
"""

import requests
import json
import uuid
from datetime import datetime
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class NequiService:
    """Servicio para integrar con la API de Nequi."""
    
    def __init__(self):
        self.api_key = settings.NEQUI_API_KEY
        self.client_id = settings.NEQUI_CLIENT_ID
        self.client_secret = settings.NEQUI_CLIENT_SECRET
        self.base_url = settings.NEQUI_BASE_URL
        self.sandbox = settings.NEQUI_SANDBOX
        
        # URLs de callback
        self.webhook_url = settings.NEQUI_WEBHOOK_URL
        self.success_url = settings.NEQUI_SUCCESS_URL
        self.cancel_url = settings.NEQUI_CANCEL_URL
        
        # Token de acceso (se obtiene mediante autenticación)
        self.access_token = None
        
    def get_access_token(self):
        """
        Obtiene un token de acceso usando las credenciales de Nequi.
        Implementa autenticación OAuth 2.0 según especificaciones de Nequi.
        """
        try:
            if self.sandbox:
                # En modo sandbox, usar token simulado
                return "sandbox_access_token_123"
            
            # URL para obtener token de acceso
            auth_url = f"{self.base_url}/auth/oauth/v2/token"
            
            # Datos para autenticación
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
            
            # Headers para autenticación
            auth_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            response = requests.post(
                auth_url,
                data=auth_data,
                headers=auth_headers,
                timeout=30
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                logger.info("Token de acceso obtenido exitosamente")
                return self.access_token
            else:
                logger.error(f"Error al obtener token: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error en autenticación Nequi: {str(e)}")
            return None
    
    def get_headers(self):
        """Obtiene los headers necesarios para las peticiones a Nequi."""
        if not self.access_token:
            self.access_token = self.get_access_token()
        
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
            'X-API-Key': self.api_key,
            'X-Client-Id': self.client_id
        }
    
    def generate_transaction_id(self):
        """Genera un ID único para la transacción."""
        return str(uuid.uuid4())
    
    def create_push_payment(self, phone_number, amount, description, reference=None):
        """
        Crea un pago push en Nequi.
        
        Args:
            phone_number (str): Número de teléfono del cliente (formato: 57XXXXXXXXXX)
            amount (float): Monto del pago
            description (str): Descripción del pago
            reference (str, optional): Referencia externa del pago
            
        Returns:
            dict: Respuesta de la API de Nequi
        """
        try:
            # Si estamos en modo sandbox, simular respuesta exitosa
            if self.sandbox:
                # Generar un transaction_id simulado
                transaction_id = reference or f"SANDBOX_{uuid.uuid4().hex[:12].upper()}"
                
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'status': 'PENDING',
                    'message': f'Pago simulado enviado al {phone_number}',
                    'sandbox': True
                }
            
            # Generar ID de transacción único
            transaction_id = reference or self.generate_transaction_id()
            
            # Preparar datos del pago según especificaciones de Nequi
            payment_data = {
                "phoneNumber": phone_number,
                "code": "NIT_1",  # Código del comercio registrado en Nequi
                "value": str(int(amount * 100)),  # Monto en centavos
                "reference1": transaction_id,
                "reference2": description[:50],  # Máximo 50 caracteres
                "reference3": "CarWash Maicao",
                "notificationUrl": self.webhook_url
            }
            
            # URL del endpoint según documentación oficial de Nequi
            endpoint = f"{self.base_url}/payments/v2/-services-paymentservice-unregisteredpayment"
            
            logger.info(f"Creando pago push Nequi para {phone_number}, monto: {amount}")
            
            # Obtener headers con autenticación
            headers = self.get_headers()
            
            # Realizar petición
            response = requests.post(
                endpoint,
                headers=headers,
                json=payment_data,
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200:
                logger.info(f"Pago push creado exitosamente: {transaction_id}")
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'nequi_transaction_id': response_data.get('transactionId'),
                    'status': 'pending',
                    'message': 'Pago push enviado al teléfono del cliente',
                    'data': response_data
                }
            else:
                logger.error(f"Error al crear pago push: {response.status_code} - {response_data}")
                return {
                    'success': False,
                    'error': response_data.get('message', 'Error desconocido'),
                    'status_code': response.status_code,
                    'data': response_data
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con Nequi API: {str(e)}")
            return {
                'success': False,
                'error': f'Error de conexión: {str(e)}',
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"Error inesperado en create_push_payment: {str(e)}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'status_code': 500
            }
    
    def check_payment_status(self, transaction_id):
        """
        Consulta el estado de un pago en Nequi.
        
        Args:
            transaction_id (str): ID de la transacción
            
        Returns:
            dict: Estado del pago
        """
        try:
            # Si estamos en modo sandbox, usar el método simulado
            if self.sandbox:
                return self.query_payment_status(transaction_id)
            
            # URL del endpoint según documentación oficial
            endpoint = f"{self.base_url}/payments/v2/-services-paymentservice-getstatuspayment"
            
            query_data = {
                "reference1": transaction_id
            }
            
            # Obtener headers con autenticación
            headers = self.get_headers()
            
            response = requests.post(
                endpoint,
                headers=headers,
                json=query_data,
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200:
                status = response_data.get('status', 'unknown')
                return {
                    'success': True,
                    'status': status,
                    'data': response_data
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('message', 'Error al consultar estado'),
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error al consultar estado del pago: {str(e)}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}',
                'status_code': 500
            }
    
    def query_payment_status(self, transaction_id):
        """
        Consulta el estado de un pago (método para sandbox)
        """
        try:
            # Si estamos en modo sandbox, simular respuesta
            if self.sandbox:
                import random
                # 70% probabilidad de éxito, 20% pendiente, 10% rechazado
                rand = random.random()
                if rand < 0.7:
                    status = 'APPROVED'
                elif rand < 0.9:
                    status = 'PENDING'
                else:
                    status = 'REJECTED'
                
                logger.info(f"Sandbox: Simulando estado {status} para transacción {transaction_id}")
                
                return {
                    'success': True,
                    'status': status,
                    'data': {
                        'transactionId': transaction_id,
                        'status': status,
                        'amount': '20000',
                        'reference1': transaction_id,
                        'sandbox': True
                    }
                }
            
            # Si no estamos en sandbox, realizar consulta real
            # URL del endpoint según documentación oficial
            endpoint = f"{self.base_url}/payments/v2/-services-paymentservice-getstatuspayment"
            
            query_data = {
                "reference1": transaction_id
            }
            
            # Obtener headers con autenticación
            headers = self.get_headers()
            
            response = requests.post(
                endpoint,
                headers=headers,
                json=query_data,
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200:
                status = response_data.get('status', 'unknown')
                return {
                    'success': True,
                    'status': status,
                    'data': response_data
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('message', 'Error al consultar estado'),
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error en query_payment_status: {str(e)}")
            return {
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }
    
    def validate_webhook_signature(self, payload, signature):
        """
        Valida la firma del webhook de Nequi.
        
        Args:
            payload (str): Cuerpo del webhook
            signature (str): Firma recibida
            
        Returns:
            bool: True si la firma es válida
        """
        # Implementar validación de firma según documentación de Nequi
        # Por ahora retornamos True para desarrollo
        return True
    
    def process_webhook_notification(self, webhook_data):
        """
        Procesa una notificación webhook de Nequi.
        
        Args:
            webhook_data (dict): Datos del webhook
            
        Returns:
            dict: Resultado del procesamiento
        """
        try:
            transaction_id = webhook_data.get('reference1')
            status = webhook_data.get('status')
            nequi_transaction_id = webhook_data.get('transactionId')
            
            logger.info(f"Procesando webhook Nequi - Transaction: {transaction_id}, Status: {status}")
            
            return {
                'success': True,
                'transaction_id': transaction_id,
                'status': status,
                'nequi_transaction_id': nequi_transaction_id,
                'processed_at': timezone.now(),
                'data': webhook_data
            }
            
        except Exception as e:
            logger.error(f"Error al procesar webhook: {str(e)}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }


# Instancia global del servicio
nequi_service = NequiService()