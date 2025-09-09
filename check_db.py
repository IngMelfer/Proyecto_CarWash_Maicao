import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
import django
django.setup()
from django.conf import settings

print(f"ENGINE: {settings.DATABASES['default']['ENGINE']}")
print(f"NAME: {settings.DATABASES['default']['NAME']}")
if 'mysql' in settings.DATABASES['default']['ENGINE']:
    print(f"HOST: {settings.DATABASES['default']['HOST']}")
    print(f"USER: {settings.DATABASES['default']['USER']}")
    print(f"PORT: {settings.DATABASES['default']['PORT']}")