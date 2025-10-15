#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from empleados.models import Empleado, Bonificacion, BonificacionObtenida
from autenticacion.models import Usuario
from django.utils import timezone
from datetime import timedelta

print('=== ASOCIANDO EMPLEADOS CON USUARIOS ===')

# Buscar el usuario de Marcos
try:
    usuario_marcos = Usuario.objects.get(email='marcos@correo.com')
    print(f'Usuario encontrado: {usuario_marcos.email} ({usuario_marcos.first_name} {usuario_marcos.last_name})')
    
    # Buscar el empleado Marcos Sierra
    empleado_marcos = Empleado.objects.filter(nombre__icontains='MARCOS', apellido__icontains='SIERRA').first()
    if empleado_marcos:
        print(f'Empleado encontrado: {empleado_marcos.nombre} {empleado_marcos.apellido}')
        
        # Asociar empleado con usuario
        empleado_marcos.usuario = usuario_marcos
        empleado_marcos.save()
        print('✅ Empleado asociado con usuario exitosamente')
        
        # Crear algunas bonificaciones obtenidas de prueba
        print('\n=== CREANDO BONIFICACIONES DE PRUEBA ===')
        
        bonificaciones = Bonificacion.objects.filter(activo=True)
        if bonificaciones.exists():
            # Crear una bonificación ganada (pendiente)
            bonificacion1 = bonificaciones.first()
            fecha_inicio = timezone.now().date() - timedelta(days=30)
            fecha_fin = timezone.now().date() - timedelta(days=1)
            
            bonificacion_ganada, created = BonificacionObtenida.objects.get_or_create(
                empleado=empleado_marcos,
                bonificacion=bonificacion1,
                fecha_inicio_periodo=fecha_inicio,
                fecha_fin_periodo=fecha_fin,
                defaults={
                    'dias_consecutivos_trabajados': bonificacion1.dias_consecutivos_requeridos or 15,
                    'servicios_realizados': bonificacion1.servicios_requeridos or 25,
                    'calificacion_promedio': bonificacion1.calificacion_minima or 4.8,
                    'estado': BonificacionObtenida.ESTADO_PENDIENTE,
                    'monto': bonificacion1.monto_bonificacion
                }
            )
            if created:
                print(f'✅ Bonificación ganada creada: {bonificacion1.nombre} - ${bonificacion_ganada.monto}')
            else:
                print(f'⚠️ Bonificación ganada ya existía: {bonificacion1.nombre}')
            
            # Crear una bonificación reclamada si hay más de una bonificación
            if bonificaciones.count() > 1:
                bonificacion2 = bonificaciones.last()
                fecha_inicio2 = timezone.now().date() - timedelta(days=60)
                fecha_fin2 = timezone.now().date() - timedelta(days=31)
                
                bonificacion_reclamada, created = BonificacionObtenida.objects.get_or_create(
                    empleado=empleado_marcos,
                    bonificacion=bonificacion2,
                    fecha_inicio_periodo=fecha_inicio2,
                    fecha_fin_periodo=fecha_fin2,
                    defaults={
                        'dias_consecutivos_trabajados': bonificacion2.dias_consecutivos_requeridos or 10,
                        'servicios_realizados': bonificacion2.servicios_requeridos or 15,
                        'calificacion_promedio': bonificacion2.calificacion_minima or 5.0,
                        'fecha_redencion': timezone.now() - timedelta(days=5),
                        'estado': BonificacionObtenida.ESTADO_REDIMIDA,
                        'monto': bonificacion2.monto_bonificacion
                    }
                )
                if created:
                    print(f'✅ Bonificación reclamada creada: {bonificacion2.nombre} - ${bonificacion_reclamada.monto}')
                else:
                    print(f'⚠️ Bonificación reclamada ya existía: {bonificacion2.nombre}')
        
        print('\n=== VERIFICACIÓN FINAL ===')
        bonificaciones_empleado = BonificacionObtenida.objects.filter(empleado=empleado_marcos)
        print(f'Total bonificaciones del empleado: {bonificaciones_empleado.count()}')
        for b in bonificaciones_empleado:
            print(f'  - {b.bonificacion.nombre}: {b.estado} - ${b.monto}')
            
    else:
        print('❌ No se encontró empleado MARCOS SIERRA')
        
except Usuario.DoesNotExist:
    print('❌ Usuario marcos@correo.com no encontrado')

print('\n=== RESUMEN FINAL ===')
empleados_con_usuario = Empleado.objects.exclude(usuario=None)
print(f'Empleados asociados con usuarios: {empleados_con_usuario.count()}')
for emp in empleados_con_usuario:
    print(f'  - {emp.nombre} {emp.apellido} -> {emp.usuario.email}')

bonificaciones_totales = BonificacionObtenida.objects.all()
print(f'Total bonificaciones obtenidas: {bonificaciones_totales.count()}')