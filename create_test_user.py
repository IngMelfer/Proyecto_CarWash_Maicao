#!/usr/bin/env python
"""
Script para crear un usuario de prueba con rol de lavador
"""

import os
import sys
import django
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

from autenticacion.models import Usuario
from empleados.models import Empleado, Cargo, TipoDocumento

def crear_usuario_lavador():
    """Crear un usuario de prueba con rol lavador"""
    
    # Datos del usuario
    email = 'lavador_test@test.com'
    password = 'test123'
    
    try:
        # Verificar si el usuario ya existe
        if Usuario.objects.filter(email=email).exists():
            print(f"El usuario {email} ya existe. Eliminando...")
            usuario_existente = Usuario.objects.get(email=email)
            # Eliminar empleado asociado si existe
            if hasattr(usuario_existente, 'empleado'):
                usuario_existente.empleado.delete()
            usuario_existente.delete()
        
        # Crear usuario
        usuario = Usuario.objects.create_user(
            email=email,
            password=password,
            first_name='Test',
            last_name='Lavador',
            rol=Usuario.ROL_LAVADOR,
            is_verified=True
        )
        print(f"Usuario creado: {usuario.email} con rol {usuario.get_rol_display()}")
        
        # Obtener cargo de lavador y tipo de documento
        try:
            cargo_lavador = Cargo.objects.get(codigo='LAV')
            print(f"Cargo encontrado: {cargo_lavador.nombre}")
        except Cargo.DoesNotExist:
            print("Error: No se encontró el cargo LAV")
            return False
            
        try:
            tipo_documento = TipoDocumento.objects.get(codigo='CC')
            print(f"Tipo documento encontrado: {tipo_documento.nombre}")
        except TipoDocumento.DoesNotExist:
            print("Error: No se encontró el tipo de documento CC")
            return False
        
        # Crear empleado asociado
        # Generar un número de documento único
        import random
        numero_documento = f"TEST{random.randint(10000, 99999)}"
        
        empleado = Empleado.objects.create(
            usuario=usuario,
            numero_documento=numero_documento,
            tipo_documento=tipo_documento,
            nombre='Test',
            apellido='Lavador',
            cargo=cargo_lavador,
            telefono='3001234567',
            direccion='Calle Test 123',
            ciudad='Maicao',
            fecha_contratacion=timezone.now().date(),
            activo=True
        )
        print(f"Empleado creado: {empleado.nombre_completo()}")
        
        print("\n=== USUARIO DE PRUEBA CREADO EXITOSAMENTE ===")
        print(f"Email: {email}")
        print(f"Contraseña: {password}")
        print(f"Rol: {usuario.get_rol_display()}")
        print(f"Cargo: {empleado.cargo.nombre}")
        print("==============================================")
        
        return True
        
    except Exception as e:
        print(f"Error al crear usuario: {str(e)}")
        return False

if __name__ == '__main__':
    crear_usuario_lavador()