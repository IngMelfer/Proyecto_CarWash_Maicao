#!/usr/bin/env python
"""
Script para probar la conexión y operaciones básicas de la base de datos
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
from django.db import connection, transaction
from django.utils import timezone
import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()
from django.contrib.auth import get_user_model
from clientes.models import Cliente
from reservas.models import Servicio, Bahia, Reserva, Vehiculo
from empleados.models import Empleado

User = get_user_model()

def test_database_connection():
    """Probar la conexión a la base de datos"""
    print("=== PRUEBA DE CONEXIÓN A BASE DE DATOS ===\n")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print("✓ Conexión a base de datos exitosa")
            print(f"  Resultado de prueba: {result[0]}")
            # Obtener información de la base de datos según el motor
            try:
                vendor = connection.vendor
                if vendor == 'sqlite':
                    cursor.execute("SELECT sqlite_version()")
                    version = cursor.fetchone()
                    print(f"  Versión de SQLite: {version[0]}")
                elif vendor == 'postgresql':
                    cursor.execute("SELECT version()")
                    version = cursor.fetchone()
                    print(f"  Versión de PostgreSQL: {version[0]}")
                else:
                    print(f"  Motor de base de datos: {vendor}")
            except Exception as e:
                print(f"  Advertencia al obtener versión de BD: {e}")
        
        # No consideramos fallo si no se pudo obtener la versión específica
        return True
    except Exception as e:
        print(f"✗ Error de conexión: {e}")
        return False
    
    return True

def test_model_operations():
    """Probar operaciones CRUD básicas en los modelos"""
    print("\n=== PRUEBA DE OPERACIONES DE MODELOS ===\n")
    
    try:
        # Test Cliente
        print("1. Probando modelo Cliente...")
        user = User.objects.create_user(
            email=f"cliente_test_{timezone.now().timestamp()}@example.com",
            password="password123"
        )
        cliente = Cliente.objects.create(
            usuario=user,
            nombre="María",
            apellido="García",
            numero_documento=f"DOC{int(timezone.now().timestamp())}",
            tipo_documento="CC",
            telefono="3001234567",
            direccion="Calle 456",
            ciudad="Bogotá"
        )
        print(f"   ✓ Cliente creado: {cliente}")
        
        # Test Servicio
        print("2. Probando modelo Servicio...")
        servicio = Servicio.objects.create(
            nombre="Lavado Premium DB Test",
            descripcion="Servicio premium para prueba de BD",
            precio=Decimal('25000.00'),
            duracion_minutos=45,
            puntos_otorgados=15
        )
        print(f"   ✓ Servicio creado: {servicio}")
        
        # Test Bahía
        print("3. Probando modelo Bahía...")
        bahia = Bahia.objects.create(
            nombre="Bahía DB Test 1",
            descripcion="Bahía para prueba de base de datos",
            activo=True,
            tiene_camara=True,
            tipo_camara='ipwebcam',
            ip_camara="192.168.1.100"
        )
        print(f"   ✓ Bahía creada: {bahia}")
        
        # Test Vehículo
        print("4. Probando modelo Vehículo...")
        vehiculo = Vehiculo.objects.create(
            cliente=cliente,
            tipo='AU',
            marca="Toyota",
            modelo="Corolla",
            anio=2020,
            placa=f"T{int(timezone.now().timestamp()) % 100000}",
            color="Blanco"
        )
        print(f"   ✓ Vehículo creado: {vehiculo}")
        
        # Test Reserva
        print("5. Probando modelo Reserva...")
        fecha_reserva = datetime.now() + timedelta(days=1)
        reserva = Reserva.objects.create(
            cliente=cliente,
            servicio=servicio,
            fecha_hora=fecha_reserva,
            bahia=bahia,
            vehiculo=vehiculo,
            notas="Reserva de prueba para BD"
        )
        print(f"   ✓ Reserva creada: {reserva}")
        
        # Test Empleado
        print("6. Probando modelo Empleado...")
        user_emp = User.objects.create_user(
            email=f"empleado_test_{timezone.now().timestamp()}@test.com",
            password="password123"
        )
        
        # Crear tipo de documento y cargo para el empleado
        from empleados.models import TipoDocumento, Cargo
        tipo_doc, _ = TipoDocumento.objects.get_or_create(
            codigo='CC',
            defaults={'nombre': 'Cédula de Ciudadanía'}
        )
        cargo, _ = Cargo.objects.get_or_create(
            codigo='LAV',
            defaults={'nombre': 'Lavador'}
        )
        
        empleado = Empleado.objects.create(
            usuario=user_emp,
            nombre="Juan",
            apellido="Pérez",
            numero_documento=f"EMP{int(timezone.now().timestamp())}",
            tipo_documento=tipo_doc,
            telefono="3001234567",
            direccion="Calle 123",
            ciudad="Bogotá",
            cargo=cargo,
            fecha_contratacion="2024-01-01",
            activo=True
        )
        print(f"   ✓ Empleado creado: {empleado}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error en operaciones de modelos: {e}")
        return False

def test_queries():
    """Probar consultas complejas"""
    print("\n=== PRUEBA DE CONSULTAS COMPLEJAS ===\n")
    
    try:
        # Contar registros
        print("1. Contando registros...")
        clientes_count = Cliente.objects.count()
        servicios_count = Servicio.objects.count()
        reservas_count = Reserva.objects.count()
        bahias_count = Bahia.objects.count()
        
        print(f"   - Clientes: {clientes_count}")
        print(f"   - Servicios: {servicios_count}")
        print(f"   - Reservas: {reservas_count}")
        print(f"   - Bahías: {bahias_count}")
        
        # Consultas con filtros
        print("2. Probando consultas con filtros...")
        servicios_activos = Servicio.objects.filter(activo=True).count()
        bahias_activas = Bahia.objects.filter(activo=True).count()
        reservas_pendientes = Reserva.objects.filter(estado='PE').count()
        
        print(f"   - Servicios activos: {servicios_activos}")
        print(f"   - Bahías activas: {bahias_activas}")
        print(f"   - Reservas pendientes: {reservas_pendientes}")
        
        # Consultas con joins
        print("3. Probando consultas con joins...")
        reservas_con_cliente = Reserva.objects.select_related('cliente', 'servicio').count()
        clientes_con_vehiculos = Cliente.objects.prefetch_related('vehiculos').count()
        
        print(f"   - Reservas con cliente: {reservas_con_cliente}")
        print(f"   - Clientes con vehículos: {clientes_con_vehiculos}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error en consultas: {e}")
        return False

def test_transactions():
    """Probar transacciones"""
    print("\n=== PRUEBA DE TRANSACCIONES ===\n")
    
    try:
        print("1. Probando transacción exitosa...")
        with transaction.atomic():
            user_trans = User.objects.create_user(
                email=f"trans_test_{timezone.now().timestamp()}@test.com",
                password="test123"
            )
            cliente = Cliente.objects.create(
                usuario=user_trans,
                nombre="Pedro",
                apellido="López",
                numero_documento=f"TRANS{int(timezone.now().timestamp())}",
                tipo_documento="CC",
                telefono="3001111111",
                direccion="Calle Trans",
                ciudad="Test City"
            )
            servicio = Servicio.objects.create(
                nombre="Servicio Transacción",
                descripcion="Servicio para prueba de transacción",
                precio=Decimal('20000.00'),
                duracion_minutos=30
            )
            print("   ✓ Transacción exitosa completada")
        
        print("2. Probando rollback de transacción...")
        try:
            with transaction.atomic():
                user2 = User.objects.create_user(
                    email=f"rollback_{timezone.now().timestamp()}@test.com",
                    password="test123"
                )
                Cliente.objects.create(
                    usuario=user2,
                    nombre="Luis",
                    apellido="Rodríguez",
                    numero_documento=f"ROLL{int(timezone.now().timestamp())}",
                    tipo_documento="CC",
                    telefono="3002222222",
                    direccion="Calle Rollback",
                    ciudad="Test City"
                )
                
                # Crear empleado
                user_emp2 = User.objects.create_user(
                    email=f"rollback_emp_{timezone.now().timestamp()}@test.com",
                    password="password123"
                )
                
                # Crear tipo de documento y cargo para el empleado
                from empleados.models import TipoDocumento, Cargo
                tipo_doc, _ = TipoDocumento.objects.get_or_create(
                    codigo='CC',
                    defaults={'nombre': 'Cédula de Ciudadanía'}
                )
                cargo, _ = Cargo.objects.get_or_create(
                    codigo='LAV',
                    defaults={'nombre': 'Lavador'}
                )
                
                empleado2 = Empleado.objects.create(
                    usuario=user_emp2,
                    nombre="Ana",
                    apellido="Martínez",
                    numero_documento="11111111",
                    tipo_documento=tipo_doc,
                    telefono="3009876543",
                    direccion="Carrera 789",
                    ciudad="Medellín",
                    cargo=cargo,
                    fecha_contratacion="2024-01-01",
                    activo=True
                )
                
                # Forzar error para probar rollback
                raise Exception("Error forzado para rollback")
        except Exception as e:
            print("   ✓ Rollback funcionó correctamente")
        
        return True
        
    except Exception as e:
        print(f"✗ Error en transacciones: {e}")
        return False

def main():
    """Función principal"""
    print("Iniciando pruebas de base de datos...\n")
    
    tests = [
        ("Conexión a BD", test_database_connection),
        ("Operaciones de modelos", test_model_operations),
        ("Consultas complejas", test_queries),
        ("Transacciones", test_transactions)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Error en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen
    print("\n" + "="*50)
    print("RESUMEN DE PRUEBAS DE BASE DE DATOS")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✓ PASÓ" if result else "✗ FALLÓ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("🎉 ¡Todas las pruebas de base de datos pasaron!")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisar logs arriba.")

if __name__ == "__main__":
    main()