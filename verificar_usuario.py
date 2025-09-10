import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

# Importar el modelo de Usuario después de configurar Django
from autenticacion.models import Usuario

# Correo del usuario a verificar
email = 'alvarezsierramelferdejesus@gmail.com'

try:
    # Buscar el usuario por email
    usuario = Usuario.objects.get(email=email)
    
    # Verificar el usuario
    if not usuario.is_verified:
        usuario.is_verified = True
        usuario.save(update_fields=['is_verified'])
        print(f'Usuario {email} ha sido verificado exitosamente.')
    else:
        print(f'El usuario {email} ya estaba verificado.')
    
    # Mostrar información del usuario
    print(f'\nInformación del usuario:')
    print(f'Email: {usuario.email}')
    print(f'Nombre: {usuario.get_full_name()}')
    print(f'Verificado: {usuario.is_verified}')
    print(f'Es staff: {usuario.is_staff}')
    print(f'Es superusuario: {usuario.is_superuser}')
    
    # Si no es superusuario, convertirlo en uno
    if not usuario.is_superuser:
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.save(update_fields=['is_staff', 'is_superuser'])
        print(f'\nEl usuario {email} ahora es superusuario.')
    
except Usuario.DoesNotExist:
    print(f'No se encontró ningún usuario con el email {email}')