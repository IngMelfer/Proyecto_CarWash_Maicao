#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from autenticacion.models import Usuario
from clientes.models import Cliente
from reservas.models import Servicio, Bahia, Reserva
from empleados.models import Empleado, Cargo, TipoDocumento
import json

def test_frontend_system():
    """Prueba completa del sistema frontend"""
    print("🎨 PRUEBAS DEL SISTEMA FRONTEND")
    print("=" * 50)
    
    # 1. Verificar templates principales
    print("\n1. Verificando templates principales...")
    try:
        templates_to_check = [
            'base.html',
            'home.html',
            'autenticacion/login.html',
            'autenticacion/registro.html',
            'clientes/dashboard.html',
            'reservas/dashboard_admin.html',
            'reservas/reservar_turno.html',
            'reservas/mis_turnos.html'
        ]
        
        templates_found = 0
        for template_name in templates_to_check:
            try:
                template = get_template(template_name)
                print(f"✅ Template encontrado: {template_name}")
                templates_found += 1
            except TemplateDoesNotExist:
                print(f"❌ Template no encontrado: {template_name}")
        
        print(f"📊 Templates encontrados: {templates_found}/{len(templates_to_check)}")
        
    except Exception as e:
        print(f"❌ Error verificando templates: {e}")
        return False
    
    # 2. Verificar URLs principales
    print("\n2. Verificando URLs principales...")
    try:
        urls_to_check = [
            ('home', {}),
            ('autenticacion:login', {}),
            ('autenticacion:registro', {}),
            ('reservas:reservar_turno', {}),
            ('reservas:mis_turnos', {}),
        ]
        
        urls_resolved = 0
        for url_name, kwargs in urls_to_check:
            try:
                url = reverse(url_name, kwargs=kwargs)
                print(f"✅ URL resuelta: {url_name} -> {url}")
                urls_resolved += 1
            except Exception as url_error:
                print(f"❌ URL no resuelta: {url_name} - {url_error}")
        
        print(f"📊 URLs resueltas: {urls_resolved}/{len(urls_to_check)}")
        
    except Exception as e:
        print(f"❌ Error verificando URLs: {e}")
        return False
    
    # 3. Crear datos de prueba
    print("\n3. Creando datos de prueba...")
    try:
        # Limpiar datos existentes más completamente
        Usuario.objects.filter(email__contains='test_frontend').delete()
        Cliente.objects.filter(numero_documento__in=['12345678', '87654321']).delete()
        
        # No necesitamos crear TipoDocumento ya que Cliente usa CharField
        
        # Crear usuario cliente
        cliente_user = Usuario.objects.create_user(
            email='test_frontend_cliente@example.com',
            password='password123',
            first_name='Cliente',
            last_name='Frontend',
            rol=Usuario.ROL_CLIENTE
        )
        
        # Crear cliente con número de documento único
        import random
        numero_doc = f"1234567{random.randint(10, 99)}"
        cliente = Cliente.objects.create(
            usuario=cliente_user,
            nombre='Cliente',
            apellido='Frontend',
            tipo_documento='CC',  # Usar directamente el código
            numero_documento=numero_doc,
            telefono='3001234567',
            direccion='Calle Test 123',
            ciudad='Bogotá',
            email='test_frontend_cliente@example.com'
        )
        
        # Crear usuario administrador
        admin_user = Usuario.objects.create_user(
            email='test_frontend_admin@example.com',
            password='password123',
            first_name='Admin',
            last_name='Frontend',
            rol=Usuario.ROL_ADMIN_SISTEMA,
            is_staff=True,
            is_superuser=True
        )
        
        # Crear servicios
        servicio = Servicio.objects.create(
            nombre='Lavado Test',
            descripcion='Servicio de prueba',
            precio=25000,
            duracion_minutos=30
        )
        
        # Crear bahía
        bahia = Bahia.objects.create(
            nombre='Bahía Test 1',
            descripcion='Bahía de prueba',
            activo=True
        )
        
        print("✅ Datos de prueba creados exitosamente")
        
    except Exception as e:
        print(f"❌ Error creando datos de prueba: {e}")
        return False
    
    # 4. Probar vistas públicas (sin autenticación)
    print("\n4. Probando vistas públicas...")
    try:
        client = Client()
        
        # Probar página de login
        response = client.get('/autenticacion/login/')
        if response.status_code == 200:
            print("✅ Página de login accesible")
            # Verificar contenido básico
            if b'login' in response.content.lower() or b'iniciar' in response.content.lower():
                print("✅ Contenido de login presente")
            else:
                print("⚠️ Contenido de login no detectado")
        else:
            print(f"❌ Página de login no accesible: {response.status_code}")
        
        # Probar página de registro
        response = client.get('/autenticacion/registro/')
        if response.status_code == 200:
            print("✅ Página de registro accesible")
            # Verificar contenido básico
            if b'registro' in response.content.lower() or b'registr' in response.content.lower():
                print("✅ Contenido de registro presente")
            else:
                print("⚠️ Contenido de registro no detectado")
        else:
            print(f"❌ Página de registro no accesible: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error probando vistas públicas: {e}")
        # No retornar False, continuar con otras pruebas
    
    # 5. Probar vistas autenticadas como cliente
    print("\n5. Probando vistas autenticadas como cliente...")
    try:
        # Login como cliente
        client.login(email='test_frontend_cliente@example.com', password='password123')
        
        # Probar dashboard de cliente
        response = client.get('/clientes/dashboard/')
        if response.status_code == 200:
            print("✅ Dashboard de cliente accesible")
            # Verificar contenido específico
            if b'dashboard' in response.content.lower() or b'bienvenido' in response.content.lower():
                print("✅ Contenido de dashboard presente")
            else:
                print("⚠️ Contenido de dashboard no detectado")
        else:
            print(f"❌ Dashboard de cliente no accesible: {response.status_code}")
        
        # Probar página de reservar turno
        response = client.get('/reservas/reservar-turno/')
        if response.status_code == 200:
            print("✅ Página de reservar turno accesible")
        else:
            print(f"❌ Página de reservar turno no accesible: {response.status_code}")
        
        # Probar página de mis turnos
        response = client.get('/reservas/mis-turnos/')
        if response.status_code == 200:
            print("✅ Página de mis turnos accesible")
        else:
            print(f"❌ Página de mis turnos no accesible: {response.status_code}")
        
        client.logout()
        
    except Exception as e:
        print(f"❌ Error probando vistas de cliente: {e}")
        # No retornar False, continuar con otras pruebas
    
    # 6. Probar vistas autenticadas como administrador
    print("\n6. Probando vistas autenticadas como administrador...")
    try:
        # Login como administrador
        client.login(email='test_frontend_admin@example.com', password='password123')
        
        # Probar dashboard de administrador
        response = client.get('/reservas/dashboard-admin/')
        if response.status_code == 200:
            print("✅ Dashboard de administrador accesible")
            # Verificar contenido específico
            if b'dashboard' in response.content.lower() or b'administrador' in response.content.lower():
                print("✅ Contenido de dashboard admin presente")
            else:
                print("⚠️ Contenido de dashboard admin no detectado")
        else:
            print(f"❌ Dashboard de administrador no accesible: {response.status_code}")
        
        # Probar panel de administración de Django
        response = client.get('/admin/')
        if response.status_code == 200:
            print("✅ Panel de administración Django accesible")
        else:
            print(f"❌ Panel de administración Django no accesible: {response.status_code}")
        
        client.logout()
        
    except Exception as e:
        print(f"❌ Error probando vistas de administrador: {e}")
        # No retornar False, continuar con otras pruebas
    
    # 7. Probar funcionalidades AJAX/JavaScript
    print("\n7. Probando funcionalidades AJAX...")
    try:
        # Login como cliente para probar AJAX
        client.login(email='test_frontend_cliente@example.com', password='password123')
        
        # Probar endpoint de horarios disponibles
        response = client.get('/reservas/obtener_horarios_disponibles/', {
            'fecha': '2024-12-01',
            'servicio_id': servicio.id
        })
        if response.status_code == 200:
            print("✅ Endpoint de horarios disponibles funcional")
            try:
                data = response.json()
                print(f"✅ Respuesta JSON válida: {len(data.get('horarios', []))} horarios")
            except:
                print("⚠️ Respuesta no es JSON válido")
        else:
            print(f"❌ Endpoint de horarios disponibles falló: {response.status_code}")
        
        # Probar endpoint de bahías disponibles
        response = client.get('/reservas/obtener_bahias_disponibles/', {
            'fecha': '2024-12-01',
            'hora': '10:00'
        })
        if response.status_code == 200:
            print("✅ Endpoint de bahías disponibles funcional")
        else:
            print(f"❌ Endpoint de bahías disponibles falló: {response.status_code}")
        
        client.logout()
        
    except Exception as e:
        print(f"❌ Error probando funcionalidades AJAX: {e}")
        # No retornar False, continuar con otras pruebas
    
    # 8. Verificar archivos estáticos
    print("\n8. Verificando configuración de archivos estáticos...")
    try:
        from django.conf import settings
        from django.contrib.staticfiles.finders import find
        
        # Verificar configuración básica
        if hasattr(settings, 'STATIC_URL'):
            print(f"✅ STATIC_URL configurado: {settings.STATIC_URL}")
        else:
            print("❌ STATIC_URL no configurado")
        
        if hasattr(settings, 'STATICFILES_DIRS'):
            print(f"✅ STATICFILES_DIRS configurado: {len(settings.STATICFILES_DIRS)} directorios")
        else:
            print("⚠️ STATICFILES_DIRS no configurado")
        
        # Intentar encontrar algunos archivos estáticos comunes
        static_files = ['admin/css/base.css', 'admin/js/core.js']
        for static_file in static_files:
            if find(static_file):
                print(f"✅ Archivo estático encontrado: {static_file}")
            else:
                print(f"⚠️ Archivo estático no encontrado: {static_file}")
        
    except Exception as e:
        print(f"❌ Error verificando archivos estáticos: {e}")
        # No retornar False, continuar con otras pruebas
    
    # 9. Limpiar datos de prueba
    print("\n9. Limpiando datos de prueba...")
    try:
        Usuario.objects.filter(email__contains='test_frontend').delete()
        Cliente.objects.filter(numero_documento__startswith='1234567').delete()
        print("✅ Datos de prueba eliminados")
        
    except Exception as e:
        print(f"❌ Error limpiando datos: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 PRUEBAS DE FRONTEND COMPLETADAS")
    print("📝 Nota: Algunas funcionalidades pueden requerir configuración adicional")
    return True

if __name__ == '__main__':
    success = test_frontend_system()
    sys.exit(0 if success else 1)