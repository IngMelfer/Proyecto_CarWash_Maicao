from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

# Create your models here.

class UsuarioManager(BaseUserManager):
    """
    Manager personalizado para el modelo Usuario.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Crea y guarda un usuario con el email y contraseña proporcionados.
        """
        if not email:
            raise ValueError(_('El Email es obligatorio'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Crea y guarda un superusuario con el email y contraseña proporcionados.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser debe tener is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser debe tener is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    """
    Modelo personalizado de usuario que utiliza email como identificador único.
    """
    username = None  # Removemos el campo username
    email = models.EmailField(_('Correo Electrónico'), unique=True)
    is_verified = models.BooleanField(_('Verificado'), default=False)
    verification_token = models.UUIDField(_('Token de Verificación'), default=uuid.uuid4, editable=False)
    token_created_at = models.DateTimeField(_('Fecha de Creación del Token'), default=timezone.now)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    class Meta:
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Retorna el nombre completo del usuario.
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        """
        Retorna el nombre corto del usuario.
        """
        return self.first_name

    def generate_verification_token(self):
        """
        Genera un nuevo token de verificación.
        """
        self.verification_token = uuid.uuid4()
        self.token_created_at = timezone.now()
        self.save(update_fields=['verification_token', 'token_created_at'])
        return self.verification_token

    def verify_email(self):
        """
        Marca el email del usuario como verificado.
        """
        self.is_verified = True
        self.save(update_fields=['is_verified'])
        return True

    def token_is_valid(self, hours=24):
        """
        Verifica si el token de verificación es válido (no ha expirado).
        """
        expiration_time = self.token_created_at + timezone.timedelta(hours=hours)
        return timezone.now() <= expiration_time
