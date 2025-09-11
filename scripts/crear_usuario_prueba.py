#!/usr/bin/env python
"""
Script para crear un usuario de prueba y asociarlo al cliente con servicios.
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')
django.setup()

# Importar después de configurar Django
from autenticacion.models import Usuario
from clientes.models import Cliente

# Obtener el cliente con servicios (ID 7 según la verificación anterior)
cliente = Cliente.objects.get(usuario__id=7)
print(f"Cliente encontrado: {cliente}")

# Crear credenciales de prueba para facilitar el acceso
usuario = cliente.usuario
usuario.username = 'cliente_test'
usuario.set_password('cliente123')
usuario.save()

print(f"Usuario actualizado: {usuario.username}")
print("Contraseña establecida: cliente123")
print("\nPuede iniciar sesión con estas credenciales para ver los servicios completados.")