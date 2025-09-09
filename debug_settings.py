import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
import django
django.setup()
from django.conf import settings

# Verificar la configuración de la base de datos
print(f"USE_MYSQL: {os.environ.get('USE_MYSQL')}")
print(f"USE_MYSQL en settings: {getattr(settings, 'USE_MYSQL', 'No definido')}")
print(f"DATABASES: {settings.DATABASES}")