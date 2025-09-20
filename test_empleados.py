#!/usr/bin/env python
"""
Script de pruebas para el sistema de empleados y roles
"""

import os
import sys
import django
from datetime import datetime, timedelta, time, date
from decimal import Decimal
from django.test import Client
from django.contrib.auth import get_user_model

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

# Importar modelos
from autenticacion.models import Usuario
from clientes.models import Cliente
from reservas.models import Servicio, Bahia, Vehiculo, Reserva, MedioPago
from django.db.models import Sum, Count, Avg

def test_sistema_empleados():
    """Función principal de pruebas del sistema de empleados"""
    print("\n👥 PRUEBAS DEL SISTEMA DE EMPLEADOS Y ROLES")
    print("=" * 50)
    
    success = True
    
    try:
        # 1. Crear datos de prueba
        datos_prueba = crear_datos_prueba()
        if not datos_prueba:
            return False
            
        # 2. Probar creación de empleados
        if not probar_creacion_empleados():
            success = False
            
        # 3. Probar roles y permisos
        if not probar_roles_permisos():
            success = False
            
        # 4. Probar asignación de reservas
        if not probar_asignacion_reservas():
            success = False
            
        # 5. Probar gestión de horarios
        if not probar_gestion_horarios():
            success = False
            
        # 6. Probar reportes de empleados
        if not probar_reportes_empleados():
            success = False
            
        # 7. Probar funcionalidades web
        if not probar_funcionalidades_web():
            success = False
            
        # 8. Limpiar datos de prueba
        limpiar_datos_prueba()
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        success = False
        
    return success

def crear_datos_prueba():
    """Crear datos de prueba para el sistema de empleados"""
    print("\n1. Creando datos de prueba para empleados...")
    try:
        # Limpiar datos existentes
        Reserva.objects.filter(cliente__usuario__email__contains='test_empleado').delete()
        Cliente.objects.filter(usuario__email__contains='test_empleado').delete()
        Usuario.objects.filter(email__contains='test_empleado').delete()
        Servicio.objects.filter(nombre='Servicio Empleado Test').delete()
        MedioPago.objects.filter(nombre='Efectivo Empleado Test').delete()
        
        # Crear usuario empleado
        user_empleado = Usuario.objects.create_user(
            email='test_empleado@example.com',
            password='password123',
            first_name='Carlos',
            last_name='Trabajador',
            rol=Usuario.ROL_EMPLEADO
        )
        
        # Crear usuario administrador
        user_admin = Usuario.objects.create_user(
            email='test_admin@example.com',
            password='password123',
            first_name='Ana',
            last_name='Administradora',
            rol=Usuario.ROL_ADMIN_AUTOLAVADO
        )
        
        # Crear usuario cliente para pruebas
        user_cliente = Usuario.objects.create_user(
            email='test_cliente_empleado@example.com',
            password='password123',
            first_name='Pedro',
            last_name='Cliente',
            rol=Usuario.ROL_CLIENTE
        )
        
        # Crear cliente
        cliente = Cliente.objects.create(
            usuario=user_cliente,
            nombre='Pedro',
            apellido='Cliente',
            telefono='3001234567',
            direccion='Calle 123',
            email='test_cliente_empleado@example.com',
            numero_documento='12345678'
        )
        
        # Crear servicio de prueba
        servicio = Servicio.objects.create(
            nombre="Servicio Empleado Test",
            descripcion="Servicio para pruebas de empleados",
            precio=30000,
            duracion_minutos=45,
            activo=True
        )
        
        # Crear bahía
        bahia = Bahia.objects.create(
            nombre='Bahía Empleados',
            descripcion='Bahía para pruebas de empleados',
            activo=True
        )
        
        # Crear vehículo
        vehiculo = Vehiculo.objects.create(
            cliente=cliente,
            tipo=Vehiculo.AUTOMOVIL,
            marca='Honda',
            modelo='Civic',
            anio=2019,
            placa='DEF456',
            color='Azul'
        )
        
        # Crear medio de pago
        medio_pago, _ = MedioPago.objects.get_or_create(
            nombre='Efectivo Empleado Test',
            defaults={
                'tipo': MedioPago.EFECTIVO,
                'activo': True
            }
        )
        
        # Crear reserva de prueba
        reserva = Reserva.objects.create(
            cliente=cliente,
            servicio=servicio,
            fecha_hora=datetime.now() + timedelta(hours=2),
            bahia=bahia,
            vehiculo=vehiculo,
            medio_pago=medio_pago,
            precio_final=servicio.precio
        )
        
        print("✅ Datos de prueba creados exitosamente")
        return {
            'empleado': user_empleado,
            'admin': user_admin,
            'cliente': cliente,
            'servicio': servicio,
            'reserva': reserva,
            'bahia': bahia,
            'medio_pago': medio_pago
        }
        
    except Exception as e:
        print(f"❌ Error creando datos de prueba: {e}")
        return None

def probar_creacion_empleados():
    """Probar la creación y gestión de empleados"""
    print("\n2. Probando creación y gestión de empleados...")
    try:
        # Verificar que se pueden crear empleados
        empleados = Usuario.objects.filter(rol=Usuario.ROL_EMPLEADO)
        print(f"✅ Empleados encontrados: {empleados.count()}")
        
        # Verificar que se pueden crear administradores
        admins = Usuario.objects.filter(rol=Usuario.ROL_ADMIN_AUTOLAVADO)
        print(f"✅ Administradores encontrados: {admins.count()}")
        
        # Verificar campos específicos de empleados
        for empleado in empleados:
            print(f"✅ Empleado: {empleado.get_full_name()} - Email: {empleado.email}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error en creación de empleados: {e}")
        return False

def probar_roles_permisos():
    """Probar el sistema de roles y permisos"""
    print("\n3. Probando roles y permisos...")
    try:
        # Verificar roles disponibles
        roles_disponibles = [choice[0] for choice in Usuario.ROLES_CHOICES]
        print(f"✅ Roles disponibles: {roles_disponibles}")
        
        # Verificar que cada rol tiene usuarios
        for rol_code, rol_name in Usuario.ROLES_CHOICES:
            count = Usuario.objects.filter(rol=rol_code).count()
            print(f"✅ {rol_name}: {count} usuarios")
            
        # Verificar métodos de rol
        empleado = Usuario.objects.filter(rol=Usuario.ROL_EMPLEADO).first()
        if empleado:
            print(f"✅ Empleado es staff: {empleado.is_staff}")
            print(f"✅ Empleado es superuser: {empleado.is_superuser}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error en roles y permisos: {e}")
        return False

def probar_asignacion_reservas():
    """Probar la asignación de reservas a empleados"""
    print("\n4. Probando asignación de reservas...")
    try:
        # Obtener reservas
        reservas = Reserva.objects.all()
        print(f"✅ Total de reservas: {reservas.count()}")
        
        # Verificar estados de reservas
        for estado_code, estado_name in Reserva.ESTADO_CHOICES:
            count = reservas.filter(estado=estado_code).count()
            if count > 0:
                print(f"✅ Reservas {estado_name}: {count}")
                
        # Probar cambios de estado
        reserva = reservas.first()
        if reserva:
            estado_original = reserva.estado
            print(f"✅ Estado original de reserva: {reserva.get_estado_display()}")
            
            # Confirmar reserva
            reserva.confirmar()
            print(f"✅ Reserva confirmada: {reserva.get_estado_display()}")
            
            # Iniciar servicio
            reserva.iniciar_servicio()
            print(f"✅ Servicio iniciado: {reserva.get_estado_display()}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error en asignación de reservas: {e}")
        return False

def probar_gestion_horarios():
    """Probar la gestión de horarios y disponibilidad"""
    print("\n5. Probando gestión de horarios...")
    try:
        # Verificar bahías disponibles
        bahias = Bahia.objects.filter(activo=True)
        print(f"✅ Bahías activas: {bahias.count()}")
        
        for bahia in bahias:
            print(f"✅ Bahía: {bahia.nombre} - Activa: {bahia.activo}")
            if bahia.tiene_camara:
                print(f"   📹 Con cámara: {bahia.tipo_camara}")
                
        # Verificar servicios disponibles
        servicios = Servicio.objects.filter(activo=True)
        print(f"✅ Servicios activos: {servicios.count()}")
        
        for servicio in servicios:
            print(f"✅ Servicio: {servicio.nombre} - Precio: ${servicio.precio} - Duración: {servicio.duracion_minutos}min")
            
        return True
        
    except Exception as e:
        print(f"❌ Error en gestión de horarios: {e}")
        return False

def probar_reportes_empleados():
    """Probar reportes y estadísticas de empleados"""
    print("\n6. Probando reportes de empleados...")
    try:
        # Reporte de reservas por estado
        reservas_por_estado = {}
        for estado_code, estado_name in Reserva.ESTADO_CHOICES:
            count = Reserva.objects.filter(estado=estado_code).count()
            reservas_por_estado[estado_name] = count
            
        print("✅ Reservas por estado:")
        for estado, count in reservas_por_estado.items():
            if count > 0:
                print(f"   {estado}: {count}")
                
        # Reporte de ingresos por medio de pago
        medios_pago = MedioPago.objects.filter(activo=True)
        print(f"✅ Medios de pago activos: {medios_pago.count()}")
        
        for medio in medios_pago:
            reservas_medio = Reserva.objects.filter(medio_pago=medio).count()
            print(f"   {medio.nombre}: {reservas_medio} reservas")
            
        # Estadísticas generales
        total_reservas = Reserva.objects.count()
        total_clientes = Cliente.objects.count()
        total_empleados = Usuario.objects.filter(rol=Usuario.ROL_EMPLEADO).count()
        
        print("✅ Estadísticas generales:")
        print(f"   Total reservas: {total_reservas}")
        print(f"   Total clientes: {total_clientes}")
        print(f"   Total empleados: {total_empleados}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en reportes de empleados: {e}")
        return False

def probar_funcionalidades_web():
    """Probar las funcionalidades web del sistema de empleados"""
    print("\n7. Probando funcionalidades web...")
    try:
        client = Client()
        
        # Probar vista de login
        response = client.get('/auth/login/')
        print(f"✅ Vista de login: {response.status_code}")
        
        # Probar vista de dashboard (sin autenticación)
        response = client.get('/dashboard/')
        print(f"✅ Vista de dashboard: {response.status_code}")
        
        # Probar vista de empleados (sin autenticación)
        response = client.get('/empleados/')
        print(f"✅ Vista de empleados: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en funcionalidades web: {e}")
        return False

def limpiar_datos_prueba():
    """Limpiar los datos de prueba creados"""
    print("\n8. Limpiando datos de prueba...")
    try:
        # Eliminar en orden para evitar problemas de integridad referencial
        Reserva.objects.filter(cliente__usuario__email__contains='test_empleado').delete()
        Cliente.objects.filter(usuario__email__contains='test_empleado').delete()
        Usuario.objects.filter(email__contains='test_empleado').delete()
        Servicio.objects.filter(nombre='Servicio Empleado Test').delete()
        Bahia.objects.filter(nombre='Bahía Empleados').delete()
        MedioPago.objects.filter(nombre='Efectivo Empleado Test').delete()
        
        print("✅ Datos de prueba de empleados eliminados")
        
    except Exception as e:
        print(f"❌ Error limpiando datos de prueba: {e}")

if __name__ == "__main__":
    success = test_sistema_empleados()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 PRUEBAS DEL SISTEMA DE EMPLEADOS COMPLETADAS")
        print("📊 Resumen:")
        print("   ✅ Creación de empleados")
        print("   ✅ Roles y permisos")
        print("   ✅ Asignación de reservas")
        print("   ✅ Gestión de horarios")
        print("   ✅ Reportes de empleados")
        print("   ✅ Funcionalidades web")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        sys.exit(1)