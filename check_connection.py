import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
import django
django.setup()
from django.db import connection

# Verificar el tipo de conexión
print(f"Tipo de conexión: {connection.__class__.__name__}")
print(f"Backend: {connection.vendor}")

# Ejecutar una consulta específica de MySQL para confirmar
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"Versión de la base de datos: {version[0]}")
except Exception as e:
    print(f"Error al ejecutar consulta: {e}")