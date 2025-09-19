from django.core.management.base import BaseCommand
from django.db import transaction
from autenticacion.models import PermisoModulo, RolPermiso, Usuario


class Command(BaseCommand):
    help = 'Crea los permisos iniciales del sistema por módulos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando creación de permisos iniciales...'))
        
        with transaction.atomic():
            # Crear permisos por módulo
            permisos_data = [
                # Bahías
                ('bahias', 'ver', 'Ver Bahías', 'Permite ver la lista de bahías y su estado'),
                ('bahias', 'crear', 'Crear Bahías', 'Permite crear nuevas bahías'),
                ('bahias', 'editar', 'Editar Bahías', 'Permite modificar información de bahías'),
                ('bahias', 'eliminar', 'Eliminar Bahías', 'Permite eliminar bahías del sistema'),
                ('bahias', 'administrar', 'Administrar Bahías', 'Acceso completo a la gestión de bahías'),
                
                # Servicios
                ('servicios', 'ver', 'Ver Servicios', 'Permite ver la lista de servicios disponibles'),
                ('servicios', 'crear', 'Crear Servicios', 'Permite crear nuevos servicios'),
                ('servicios', 'editar', 'Editar Servicios', 'Permite modificar servicios existentes'),
                ('servicios', 'eliminar', 'Eliminar Servicios', 'Permite eliminar servicios del sistema'),
                ('servicios', 'administrar', 'Administrar Servicios', 'Acceso completo a la gestión de servicios'),
                
                # Reservas
                ('reservas', 'ver', 'Ver Reservas', 'Permite ver las reservas del sistema'),
                ('reservas', 'crear', 'Crear Reservas', 'Permite crear nuevas reservas'),
                ('reservas', 'editar', 'Editar Reservas', 'Permite modificar reservas existentes'),
                ('reservas', 'eliminar', 'Eliminar Reservas', 'Permite cancelar/eliminar reservas'),
                ('reservas', 'administrar', 'Administrar Reservas', 'Acceso completo a la gestión de reservas'),
                
                # Empleados
                ('empleados', 'ver', 'Ver Empleados', 'Permite ver la lista de empleados'),
                ('empleados', 'crear', 'Crear Empleados', 'Permite registrar nuevos empleados'),
                ('empleados', 'editar', 'Editar Empleados', 'Permite modificar información de empleados'),
                ('empleados', 'eliminar', 'Eliminar Empleados', 'Permite eliminar empleados del sistema'),
                ('empleados', 'administrar', 'Administrar Empleados', 'Acceso completo a la gestión de empleados'),
                
                # Clientes
                ('clientes', 'ver', 'Ver Clientes', 'Permite ver la lista de clientes'),
                ('clientes', 'crear', 'Crear Clientes', 'Permite registrar nuevos clientes'),
                ('clientes', 'editar', 'Editar Clientes', 'Permite modificar información de clientes'),
                ('clientes', 'eliminar', 'Eliminar Clientes', 'Permite eliminar clientes del sistema'),
                ('clientes', 'administrar', 'Administrar Clientes', 'Acceso completo a la gestión de clientes'),
                
                # Notificaciones
                ('notificaciones', 'ver', 'Ver Notificaciones', 'Permite ver notificaciones del sistema'),
                ('notificaciones', 'crear', 'Crear Notificaciones', 'Permite crear nuevas notificaciones'),
                ('notificaciones', 'editar', 'Editar Notificaciones', 'Permite modificar notificaciones'),
                ('notificaciones', 'eliminar', 'Eliminar Notificaciones', 'Permite eliminar notificaciones'),
                ('notificaciones', 'administrar', 'Administrar Notificaciones', 'Acceso completo a notificaciones'),
                
                # Reportes
                ('reportes', 'ver', 'Ver Reportes', 'Permite acceder a reportes y estadísticas'),
                ('reportes', 'crear', 'Crear Reportes', 'Permite generar nuevos reportes'),
                ('reportes', 'editar', 'Editar Reportes', 'Permite modificar reportes existentes'),
                ('reportes', 'eliminar', 'Eliminar Reportes', 'Permite eliminar reportes'),
                ('reportes', 'administrar', 'Administrar Reportes', 'Acceso completo a reportes'),
                
                # Configuración
                ('configuracion', 'ver', 'Ver Configuración', 'Permite ver configuraciones del sistema'),
                ('configuracion', 'crear', 'Crear Configuración', 'Permite crear nuevas configuraciones'),
                ('configuracion', 'editar', 'Editar Configuración', 'Permite modificar configuraciones'),
                ('configuracion', 'eliminar', 'Eliminar Configuración', 'Permite eliminar configuraciones'),
                ('configuracion', 'administrar', 'Administrar Configuración', 'Acceso completo a configuración'),
                
                # Inventario
                ('inventario', 'ver', 'Ver Inventario', 'Permite ver el inventario de productos'),
                ('inventario', 'crear', 'Crear Inventario', 'Permite agregar productos al inventario'),
                ('inventario', 'editar', 'Editar Inventario', 'Permite modificar inventario'),
                ('inventario', 'eliminar', 'Eliminar Inventario', 'Permite eliminar productos del inventario'),
                ('inventario', 'administrar', 'Administrar Inventario', 'Acceso completo al inventario'),
                
                # Facturación
                ('facturacion', 'ver', 'Ver Facturación', 'Permite ver facturas y pagos'),
                ('facturacion', 'crear', 'Crear Facturación', 'Permite generar facturas'),
                ('facturacion', 'editar', 'Editar Facturación', 'Permite modificar facturas'),
                ('facturacion', 'eliminar', 'Eliminar Facturación', 'Permite anular facturas'),
                ('facturacion', 'administrar', 'Administrar Facturación', 'Acceso completo a facturación'),
            ]
            
            # Crear permisos
            permisos_creados = 0
            for modulo, accion, nombre, descripcion in permisos_data:
                permiso, created = PermisoModulo.objects.get_or_create(
                    modulo=modulo,
                    accion=accion,
                    defaults={
                        'nombre': nombre,
                        'descripcion': descripcion,
                        'activo': True
                    }
                )
                if created:
                    permisos_creados += 1
                    self.stdout.write(f'  ✓ Creado: {permiso}')
            
            self.stdout.write(
                self.style.SUCCESS(f'Permisos creados: {permisos_creados}')
            )
            
            # Asignar permisos por defecto a roles
            self.asignar_permisos_por_rol()
    
    def asignar_permisos_por_rol(self):
        """Asigna permisos por defecto a cada rol"""
        self.stdout.write('Asignando permisos por defecto a roles...')
        
        # Definir permisos por rol
        permisos_por_rol = {
            Usuario.ROL_ADMIN_SISTEMA: 'todos',  # Todos los permisos
            Usuario.ROL_ADMIN_AUTOLAVADO: [
                # Bahías - todos los permisos
                ('bahias', ['ver', 'crear', 'editar', 'eliminar', 'administrar']),
                # Servicios - todos los permisos
                ('servicios', ['ver', 'crear', 'editar', 'eliminar', 'administrar']),
                # Reservas - todos los permisos
                ('reservas', ['ver', 'crear', 'editar', 'eliminar', 'administrar']),
                # Empleados - ver, crear, editar
                ('empleados', ['ver', 'crear', 'editar']),
                # Clientes - todos los permisos
                ('clientes', ['ver', 'crear', 'editar', 'eliminar', 'administrar']),
                # Notificaciones - todos los permisos
                ('notificaciones', ['ver', 'crear', 'editar', 'eliminar', 'administrar']),
                # Reportes - ver, crear
                ('reportes', ['ver', 'crear']),
                # Configuración - ver, editar
                ('configuracion', ['ver', 'editar']),
                # Inventario - todos los permisos
                ('inventario', ['ver', 'crear', 'editar', 'eliminar', 'administrar']),
                # Facturación - todos los permisos
                ('facturacion', ['ver', 'crear', 'editar', 'eliminar', 'administrar']),
            ],
            Usuario.ROL_GERENTE: [
                # Bahías - ver, editar
                ('bahias', ['ver', 'editar']),
                # Servicios - ver, crear, editar
                ('servicios', ['ver', 'crear', 'editar']),
                # Reservas - ver, crear, editar
                ('reservas', ['ver', 'crear', 'editar']),
                # Empleados - ver
                ('empleados', ['ver']),
                # Clientes - ver, crear, editar
                ('clientes', ['ver', 'crear', 'editar']),
                # Notificaciones - ver, crear
                ('notificaciones', ['ver', 'crear']),
                # Reportes - ver, crear
                ('reportes', ['ver', 'crear']),
                # Inventario - ver, editar
                ('inventario', ['ver', 'editar']),
                # Facturación - ver, crear
                ('facturacion', ['ver', 'crear']),
            ],
            Usuario.ROL_EMPLEADO: [
                # Bahías - ver
                ('bahias', ['ver']),
                # Servicios - ver
                ('servicios', ['ver']),
                # Reservas - ver, crear, editar
                ('reservas', ['ver', 'crear', 'editar']),
                # Clientes - ver, crear
                ('clientes', ['ver', 'crear']),
                # Notificaciones - ver
                ('notificaciones', ['ver']),
                # Inventario - ver
                ('inventario', ['ver']),
            ],
            Usuario.ROL_CLIENTE: [
                # Reservas - ver (solo sus propias reservas), crear
                ('reservas', ['ver', 'crear']),
                # Servicios - ver
                ('servicios', ['ver']),
                # Notificaciones - ver (solo sus propias notificaciones)
                ('notificaciones', ['ver']),
            ]
        }
        
        asignaciones_creadas = 0
        
        for rol, permisos in permisos_por_rol.items():
            if permisos == 'todos':
                # Asignar todos los permisos al admin del sistema
                todos_permisos = PermisoModulo.objects.filter(activo=True)
                for permiso in todos_permisos:
                    rol_permiso, created = RolPermiso.objects.get_or_create(
                        rol=rol,
                        permiso=permiso,
                        defaults={'activo': True}
                    )
                    if created:
                        asignaciones_creadas += 1
            else:
                # Asignar permisos específicos
                for modulo, acciones in permisos:
                    for accion in acciones:
                        try:
                            permiso = PermisoModulo.objects.get(
                                modulo=modulo,
                                accion=accion,
                                activo=True
                            )
                            rol_permiso, created = RolPermiso.objects.get_or_create(
                                rol=rol,
                                permiso=permiso,
                                defaults={'activo': True}
                            )
                            if created:
                                asignaciones_creadas += 1
                        except PermisoModulo.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Permiso no encontrado: {modulo} - {accion}'
                                )
                            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Asignaciones de permisos creadas: {asignaciones_creadas}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS('¡Permisos iniciales configurados correctamente!')
        )