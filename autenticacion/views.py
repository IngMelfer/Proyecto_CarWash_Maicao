from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.views.generic import View, TemplateView
from django.urls import reverse
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import RegistroUsuarioSerializer, LoginSerializer, UsuarioSerializer
from .models import Usuario
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import uuid

# Create your views here.

class RecuperarPasswordView(View):
    """Vista para solicitar recuperación de contraseña"""
    
    def get(self, request):
        return render(request, 'autenticacion/recuperar_password.html')
    
    def post(self, request):
        email = request.POST.get('email')
        
        try:
            usuario = Usuario.objects.get(email=email)
            
            # Generar token de recuperación
            token = str(uuid.uuid4())
            usuario.reset_password_token = token
            usuario.reset_password_token_created = timezone.now()
            usuario.save()
            
            # Enviar correo de recuperación
            self.enviar_correo_recuperacion(usuario, token)
            
            messages.success(request, 'Se ha enviado un correo con instrucciones para recuperar tu contraseña.')
            return redirect('autenticacion:login')
            
        except Usuario.DoesNotExist:
            messages.error(request, 'No existe una cuenta con ese correo electrónico.')
            return redirect('autenticacion:recuperar_password')
    
    def enviar_correo_recuperacion(self, usuario, token):
        """Envía un correo de recuperación de contraseña al usuario"""
        subject = 'Recuperación de contraseña - Premium Car Detailing'
        reset_url = f"{settings.SITE_URL}{reverse('autenticacion:reset_password', args=[token])}"
        
        # Contenido HTML
        html_message = render_to_string('autenticacion/email_reset_password.html', {
            'usuario': usuario,
            'reset_url': reset_url
        })
        
        # Contenido texto plano
        plain_message = strip_tags(html_message)
        
        # Enviar correo
        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [usuario.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error al enviar correo: {e}")
            return False


class ResetPasswordView(View):
    """Vista para restablecer contraseña"""
    
    def get(self, request, token):
        try:
            usuario = Usuario.objects.get(reset_password_token=token)
            
            # Verificar si el token ha expirado (24 horas)
            if usuario.reset_password_token_created and \
               (timezone.now() - usuario.reset_password_token_created).total_seconds() > 86400:
                messages.error(request, 'El enlace de recuperación ha expirado. Por favor solicita uno nuevo.')
                return redirect('autenticacion:recuperar_password')
            
            return render(request, 'autenticacion/reset_password.html')
            
        except Usuario.DoesNotExist:
            messages.error(request, 'El enlace de recuperación es inválido.')
            return redirect('autenticacion:recuperar_password')
    
    def post(self, request, token):
        try:
            usuario = Usuario.objects.get(reset_password_token=token)
            
            # Verificar si el token ha expirado (24 horas)
            if usuario.reset_password_token_created and \
               (timezone.now() - usuario.reset_password_token_created).total_seconds() > 86400:
                messages.error(request, 'El enlace de recuperación ha expirado. Por favor solicita uno nuevo.')
                return redirect('autenticacion:recuperar_password')
            
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')
            
            if password != password_confirm:
                messages.error(request, 'Las contraseñas no coinciden.')
                return render(request, 'autenticacion/reset_password.html')
            
            # Cambiar contraseña
            usuario.set_password(password)
            usuario.reset_password_token = None
            usuario.reset_password_token_created = None
            usuario.save()
            
            messages.success(request, 'Tu contraseña ha sido restablecida exitosamente. Ahora puedes iniciar sesión.')
            return redirect('autenticacion:login')
            
        except Usuario.DoesNotExist:
            messages.error(request, 'El enlace de recuperación es inválido.')
            return redirect('autenticacion:recuperar_password')

class RegistroUsuarioView(View):
    """Vista para el registro de nuevos usuarios"""
    
    def get(self, request):
        # Si el usuario ya está autenticado, redirigir al inicio
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'autenticacion/registro.html')
    
    def post(self, request):
        # Crear un diccionario con los datos del formulario
        data = {
            'email': request.POST.get('email'),
            'telefono': request.POST.get('telefono'),
            'password': request.POST.get('password'),
            'password_confirm': request.POST.get('password_confirm'),
            'nombre': request.POST.get('nombre'),
            'apellido': request.POST.get('apellido'),
            'tipo_documento': request.POST.get('tipo_documento'),
            'numero_documento': request.POST.get('numero_documento'),
            'direccion': request.POST.get('direccion'),
            'ciudad': request.POST.get('ciudad'),
            'fecha_nacimiento': request.POST.get('fecha_nacimiento'),
            'notificaciones_email': request.POST.get('notificaciones_email') == 'on',
            'notificaciones_sms': request.POST.get('notificaciones_sms') == 'on',
            'notificaciones_whatsapp': request.POST.get('notificaciones_whatsapp') == 'on',
        }
        
        serializer = RegistroUsuarioSerializer(data=data)
        if serializer.is_valid():
            usuario = serializer.save()
            
            # Generar token de verificación
            token = usuario.generate_verification_token()
            
            # Enviar correo de verificación
            self.enviar_correo_verificacion(usuario, token)
            
            messages.success(request, 'Usuario registrado exitosamente. Por favor verifica tu correo electrónico.')
            return redirect('autenticacion:login')
        else:
            # Mostrar errores de validación
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            return render(request, 'autenticacion/registro.html', {'form_data': data})
    
    def enviar_correo_verificacion(self, usuario, token):
        """Envía un correo de verificación al usuario"""
        subject = 'Verifica tu cuenta de Premium Car Detailing'
        verification_url = f"{settings.SITE_URL}{reverse('autenticacion:verificar_email', args=[token])}"
        
        # Contenido HTML
        html_message = render_to_string('autenticacion/email_verificacion.html', {
            'usuario': usuario,
            'verification_url': verification_url
        })
        
        # Contenido texto plano
        plain_message = strip_tags(html_message)
        
        # Enviar correo
        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [usuario.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error al enviar correo: {e}")
            return False


class RegistroUsuarioAPIView(APIView):
    """Vista API para el registro de nuevos usuarios"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegistroUsuarioSerializer(data=request.data)
        if serializer.is_valid():
            usuario = serializer.save()
            
            # Generar token de verificación
            token = usuario.generate_verification_token()
            
            # Enviar correo de verificación
            self.enviar_correo_verificacion(usuario, token)
            
            # Crear token de autenticación
            auth_token, created = Token.objects.get_or_create(user=usuario)
            
            return Response({
                'token': auth_token.key,
                'usuario': UsuarioSerializer(usuario).data,
                'mensaje': 'Usuario registrado exitosamente. Por favor verifica tu correo electrónico.'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def enviar_correo_verificacion(self, usuario, token):
        """Envía un correo de verificación al usuario"""
        subject = 'Verifica tu cuenta de Premium Car Detailing'
        verification_url = f"{settings.SITE_URL}{reverse('autenticacion:verificar_email', args=[token])}"
        
        # Contenido HTML
        html_message = render_to_string('autenticacion/email_verificacion.html', {
            'usuario': usuario,
            'verification_url': verification_url
        })
        
        # Contenido texto plano
        plain_message = strip_tags(html_message)
        
        # Enviar correo
        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [usuario.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error al enviar correo: {e}")
            return False
    
    def enviar_correo_verificacion(self, usuario, token):
        """Envía un correo de verificación al usuario"""
        subject = 'Verifica tu cuenta de Autolavados'
        verification_url = f"{settings.FRONTEND_URL}/verificar-email/{token}/"
        
        # Contenido HTML
        html_message = render_to_string('autenticacion/email_verificacion.html', {
            'usuario': usuario,
            'verification_url': verification_url
        })
        
        # Contenido texto plano
        plain_message = strip_tags(html_message)
        
        # Enviar correo
        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [usuario.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error al enviar correo: {e}")
            return False


class VerificarEmailView(View):
    """Vista para verificar el email del usuario"""
    
    def get(self, request, token):
        try:
            usuario = Usuario.objects.get(verification_token=token)
            
            # Verificar si el token ha expirado
            if not usuario.token_is_valid():
                messages.error(request, 'El token de verificación ha expirado.')
                return render(request, 'autenticacion/verificacion_email.html', {
                    'success': False,
                    'error_message': 'El token de verificación ha expirado.'
                })
            
            # Verificar el email
            usuario.verify_email()
            
            messages.success(request, 'Email verificado exitosamente.')
            return render(request, 'autenticacion/verificacion_email.html', {
                'success': True
            })
            
        except Usuario.DoesNotExist:
            messages.error(request, 'Token de verificación inválido.')
            return render(request, 'autenticacion/verificacion_email.html', {
                'success': False,
                'error_message': 'Token de verificación inválido.'
            })


class LoginView(View):
    """Vista para el inicio de sesión"""
    
    def get(self, request):
        # Si el usuario ya está autenticado, redirigir al inicio
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'autenticacion/login.html')
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me') == 'on'
        
        usuario = authenticate(request, username=email, password=password)
        
        if usuario is not None:
            # Verificar si el email está verificado
            if not usuario.is_verified:
                messages.warning(request, 'Por favor verifica tu correo electrónico antes de iniciar sesión.')
                return redirect('autenticacion:login')
            
            login(request, usuario)
            
            # Configurar la sesión para que expire según remember_me
            if not remember_me:
                request.session.set_expiry(0)  # Expira al cerrar el navegador
            
            # Crear o obtener token para API
            token, created = Token.objects.get_or_create(user=usuario)
            
            # Redirigir a la página de inicio o a next si existe
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Credenciales inválidas. Por favor intenta de nuevo.')
            return redirect('autenticacion:login')


class LoginAPIView(APIView):
    """Vista API para el inicio de sesión"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            usuario = authenticate(request, username=email, password=password)
            
            if usuario is not None:
                # Verificar si el email está verificado
                if not usuario.is_verified:
                    return Response({
                        'error': 'Por favor verifica tu correo electrónico antes de iniciar sesión.'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                login(request, usuario)
                
                # Crear o obtener token
                token, created = Token.objects.get_or_create(user=usuario)
                
                return Response({
                    'token': token.key,
                    'usuario': UsuarioSerializer(usuario).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Credenciales inválidas'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(View):
    """Vista para cerrar sesión"""
    
    def get(self, request):
        if request.user.is_authenticated:
            # Eliminar token
            try:
                request.user.auth_token.delete()
            except:
                pass
            
            # Cerrar sesión
            logout(request)
            messages.success(request, 'Sesión cerrada exitosamente')
        
        return redirect('autenticacion:login')


class LogoutAPIView(APIView):
    """Vista API para cerrar sesión"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Eliminar token
        try:
            request.user.auth_token.delete()
        except:
            pass
        
        # Cerrar sesión
        logout(request)
        
        return Response({
            'mensaje': 'Sesión cerrada exitosamente'
        }, status=status.HTTP_200_OK)


class PerfilUsuarioView(View):
    """Vista para ver y actualizar el perfil del usuario"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('autenticacion:login')
        
        return render(request, 'autenticacion/perfil.html', {
            'usuario': request.user,
            'cliente': request.user.cliente
        })
    
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('autenticacion:login')
        
        # Crear un diccionario con los datos del formulario
        data = {}
        
        # Solo incluir campos que no sean nulos
        if request.POST.get('telefono'):
            data['telefono'] = request.POST.get('telefono')
        if request.POST.get('direccion'):
            data['direccion'] = request.POST.get('direccion')
        if request.POST.get('ciudad'):
            data['ciudad'] = request.POST.get('ciudad')
        if request.POST.get('tipo_documento'):
            data['tipo_documento'] = request.POST.get('tipo_documento')
        if request.POST.get('numero_documento'):
            data['numero_documento'] = request.POST.get('numero_documento')
        if request.POST.get('notificaciones_email'):
            data['notificaciones_email'] = request.POST.get('notificaciones_email') == 'on'
        
        # Manejar la foto de perfil si se proporciona
        if 'foto_perfil' in request.FILES and request.FILES['foto_perfil']:
            data['foto_perfil'] = request.FILES['foto_perfil']
            print(f"Foto de perfil recibida: {request.FILES['foto_perfil']}")
        else:
            print("No se recibió foto de perfil")
        
        # Actualizar los campos del cliente directamente
        cliente = request.user.cliente
        
        # Solo actualizar campos que no sean nulos
        if request.POST.get('nombre'):
            cliente.nombre = request.POST.get('nombre')
        if request.POST.get('apellido'):
            cliente.apellido = request.POST.get('apellido')
        if request.POST.get('telefono'):
            cliente.telefono = request.POST.get('telefono')
        if request.POST.get('direccion'):
            cliente.direccion = request.POST.get('direccion')
        if request.POST.get('ciudad'):
            cliente.ciudad = request.POST.get('ciudad')
        if request.POST.get('tipo_documento'):
            cliente.tipo_documento = request.POST.get('tipo_documento')
        if request.POST.get('numero_documento'):
            cliente.numero_documento = request.POST.get('numero_documento')
        if 'notificaciones_email' in request.POST:
            cliente.recibir_notificaciones = request.POST.get('notificaciones_email') == 'on'
        
        # Solo guardar si se está actualizando más que solo la foto
        if any([request.POST.get(field) for field in ['nombre', 'apellido', 'telefono', 'direccion', 'ciudad', 'tipo_documento', 'numero_documento', 'notificaciones_email']]):
            cliente.save()
        
        # Actualizar el usuario con el serializador para manejar la foto de perfil
        serializer = UsuarioSerializer(request.user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Perfil actualizado exitosamente')
            return redirect('autenticacion:perfil')
        else:
            # Mostrar errores de validación
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            return render(request, 'autenticacion/perfil.html', {
                'usuario': request.user,
                'cliente': request.user.cliente,
                'form_data': data
            })


class PerfilUsuarioAPIView(APIView):
    """Vista API para ver y actualizar el perfil del usuario"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        serializer = UsuarioSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CambiarPasswordView(View):
    """Vista para cambiar la contraseña del usuario"""
    
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('autenticacion:login')
        
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        new_password_confirm = request.POST.get('new_password_confirm')
        
        # Validar que la contraseña actual sea correcta
        if not request.user.check_password(current_password):
            messages.error(request, 'La contraseña actual es incorrecta')
            return redirect('autenticacion:perfil')
        
        # Validar que las nuevas contraseñas coincidan
        if new_password != new_password_confirm:
            messages.error(request, 'Las nuevas contraseñas no coinciden')
            return redirect('autenticacion:perfil')
        
        # Validar que la nueva contraseña cumpla con los requisitos
        if len(new_password) < 8:
            messages.error(request, 'La nueva contraseña debe tener al menos 8 caracteres')
            return redirect('autenticacion:perfil')
        
        # Cambiar la contraseña
        request.user.set_password(new_password)
        request.user.save()
        
        # Actualizar la sesión para que el usuario no tenga que iniciar sesión nuevamente
        update_session_auth_hash(request, request.user)
        
        messages.success(request, 'Contraseña cambiada exitosamente')
        return redirect('autenticacion:perfil')
