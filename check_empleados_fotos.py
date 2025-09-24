#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from empleados.models import Empleado

def main():
    empleados = Empleado.objects.filter(activo=True)
    print(f'Total empleados activos: {empleados.count()}')
    
    for emp in empleados:
        if emp.fotografia:
            print(f'- {emp.nombre_completo()}: {emp.fotografia.url}')
        else:
            print(f'- {emp.nombre_completo()}: Sin foto')

if __name__ == '__main__':
    main()