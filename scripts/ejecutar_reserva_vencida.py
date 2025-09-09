# Script para ejecutar crear_reserva_vencida.py desde el shell de Django
import os
import sys
import django

# Agregar el directorio del proyecto al path de Python
sys.path.append('.')

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

# Importar el script
exec(open('scripts/crear_reserva_vencida.py').read())