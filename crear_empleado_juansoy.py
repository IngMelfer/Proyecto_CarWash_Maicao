#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from autenticacion.models import Usuario
from empleados.models import Empleado, Cargo, TipoDocumento
from datetime import date

def crear_empleado_juansoy():
    print("=== CREANDO EMPLEADO PARA JUANSOY ===")
    
    try:
        # Buscar el usuario
        usuario = Usuario.objects.filter(email='juansoy@correo.com').first()
        if not usuario:
            print("❌ Usuario juansoy@correo.com no encontrado")
            return
        
        print(f"✓ Usuario encontrado: {usuario.email} (ID: {usuario.id})")
        
        # Verificar si ya tiene empleado
        empleado_existente = Empleado.objects.filter(usuario=usuario).first()
        if empleado_existente:
            print(f"⚠️  El usuario ya tiene un empleado asociado: {empleado_existente}")
            return
        
        # Buscar o crear tipo de documento (CC - Cédula de Ciudadanía)
        tipo_doc, created = TipoDocumento.objects.get_or_create(
            codigo='CC',
            defaults={
                'nombre': 'Cédula de Ciudadanía',
                'activo': True
            }
        )
        if created:
            print(f"✓ Tipo de documento creado: {tipo_doc}")
        else:
            print(f"✓ Tipo de documento encontrado: {tipo_doc}")
        
        # Buscar o crear cargo de Lavador
        cargo, created = Cargo.objects.get_or_create(
            codigo='LAV',
            defaults={
                'nombre': 'Lavador',
                'descripcion': 'Empleado encargado del lavado de vehículos',
                'activo': True
            }
        )
        if created:
            print(f"✓ Cargo creado: {cargo}")
        else:
            print(f"✓ Cargo encontrado: {cargo}")
        
        # Crear el empleado
        empleado = Empleado.objects.create(
            usuario=usuario,
            numero_documento='1234567890',  # Documento temporal
            tipo_documento=tipo_doc,
            nombre='Juan',
            apellido='Soy',
            email_personal=usuario.email,
            telefono='3001234567',
            direccion='Calle 123 #45-67',
            ciudad='Maicao',
            fecha_nacimiento=date(1990, 1, 1),
            cargo=cargo,
            rol=Empleado.ROL_LAVADOR,
            disponible=True,
            fecha_contratacion=date.today(),
            activo=True
        )
        
        print(f"✅ Empleado creado exitosamente:")
        print(f"   - ID: {empleado.id}")
        print(f"   - Nombre: {empleado.nombre_completo()}")
        print(f"   - Documento: {empleado.numero_documento}")
        print(f"   - Cargo: {empleado.cargo}")
        print(f"   - Rol: {empleado.rol}")
        print(f"   - Usuario asociado: {empleado.usuario.email}")
        
        # Actualizar username del usuario si está vacío
        if not usuario.username:
            usuario.username = empleado.numero_documento
            usuario.save()
            print(f"✓ Username actualizado: {usuario.username}")
        
        print("\n🎉 ¡Empleado creado correctamente! Ahora el usuario puede acceder al dashboard.")
        
    except Exception as e:
        print(f"❌ Error al crear empleado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    crear_empleado_juansoy()