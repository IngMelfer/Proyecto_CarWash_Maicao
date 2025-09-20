import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from django.db import connection

def check_table_structure():
    with connection.cursor() as cursor:
        print("=== ESTRUCTURA DE TABLA empleados_empleado ===")
        cursor.execute("DESCRIBE empleados_empleado")
        columns = cursor.fetchall()
        for column in columns:
            print(f"Campo: {column[0]}, Tipo: {column[1]}, Null: {column[2]}, Key: {column[3]}, Default: {column[4]}")
        
        print("\n=== ESTRUCTURA DE TABLA autenticacion_usuario ===")
        cursor.execute("DESCRIBE autenticacion_usuario")
        columns = cursor.fetchall()
        for column in columns:
            print(f"Campo: {column[0]}, Tipo: {column[1]}, Null: {column[2]}, Key: {column[3]}, Default: {column[4]}")

if __name__ == "__main__":
    check_table_structure()