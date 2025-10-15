#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from empleados.models import Bonificacion, BonificacionObtenida, Empleado
from autenticacion.models import Usuario

print('=== BONIFICACIONES ACTIVAS ===')
bonificaciones = Bonificacion.objects.filter(activo=True)
print(f'Total bonificaciones activas: {bonificaciones.count()}')
for b in bonificaciones:
    print(f'- {b.nombre}: {b.descripcion}')

print('\n=== EMPLEADOS ===')
empleados = Empleado.objects.all()
print(f'Total empleados: {empleados.count()}')
for e in empleados:
    print(f'- {e.nombre} {e.apellido} (Usuario: {e.usuario.email}, Rol Usuario: {e.usuario.rol}, Rol Empleado: {e.rol})')

print('\n=== BONIFICACIONES OBTENIDAS ===')
bonificaciones_obtenidas = BonificacionObtenida.objects.all()
print(f'Total bonificaciones obtenidas: {bonificaciones_obtenidas.count()}')
for bo in bonificaciones_obtenidas:
    print(f'- {bo.empleado.nombre} {bo.empleado.apellido}: {bo.bonificacion.nombre} - Estado: {bo.estado}')

print('\n=== VERIFICAR USUARIO MARCOS SIERRA ===')
try:
    usuario_marcos = Usuario.objects.get(email='marcos@correo.com')
    empleado_marcos = Empleado.objects.get(usuario=usuario_marcos)
    print(f'Usuario encontrado: {usuario_marcos.email}')
    print(f'Empleado: {empleado_marcos.nombre} {empleado_marcos.apellido}')
    print(f'Rol Usuario: {usuario_marcos.rol}')
    print(f'Rol Empleado: {empleado_marcos.rol}')
    print(f'¿Es lavador? {empleado_marcos.rol == Empleado.ROL_LAVADOR}')
    
    # Verificar bonificaciones del empleado
    bonificaciones_marcos = BonificacionObtenida.objects.filter(empleado=empleado_marcos)
    print(f'Bonificaciones obtenidas por Marcos: {bonificaciones_marcos.count()}')
    for b in bonificaciones_marcos:
        print(f'  - {b.bonificacion.nombre}: {b.estado}')
        
except Usuario.DoesNotExist:
    print('Usuario marcos@correo.com no encontrado')
    # Buscar cualquier usuario con nombre Marcos
    usuarios_marcos = Usuario.objects.filter(first_name__icontains='marcos')
    print(f'Usuarios con nombre Marcos encontrados: {usuarios_marcos.count()}')
    for u in usuarios_marcos:
        print(f'  - {u.email} ({u.first_name} {u.last_name})')
except Empleado.DoesNotExist:
    print('Empleado asociado a marcos@correo.com no encontrado')