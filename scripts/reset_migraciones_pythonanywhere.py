#!/usr/bin/env python
"""
Script para resetear migraciones en PythonAnywhere de forma segura.
Ejecutar desde el directorio raíz del proyecto: python scripts/reset_migraciones_pythonanywhere.py
"""

import os
import sys
import subprocess
from datetime import datetime

def ejecutar_comando(comando, descripcion):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n🔄 {descripcion}")
    print(f"Comando: {comando}")
    
    try:
        result = subprocess.run(comando, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Éxito: {descripcion}")
            if result.stdout.strip():
                print(f"Salida:\n{result.stdout}")
        else:
            print(f"❌ Error en: {descripcion}")
            print(f"Error:\n{result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción en: {descripcion}")
        print(f"Error: {e}")
        return False
    
    return True

def reset_migraciones():
    """Proceso completo de reset de migraciones"""
    print("🚀 INICIANDO RESET DE MIGRACIONES PARA PYTHONANYWHERE")
    print("=" * 60)
    
    # Lista de apps del proyecto
    apps = [
        'autenticacion',
        'clientes', 
        'empleados',
        'reservas',
        'notificaciones',
        'dashboard_gerente',
        'dashboard_publico'
    ]
    
    # Paso 1: Verificar estado actual
    print("\n📊 PASO 1: Verificando estado actual de migraciones")
    if not ejecutar_comando("python manage.py showmigrations", "Mostrar estado de migraciones"):
        return False
    
    # Paso 2: Marcar todas las migraciones como no aplicadas (fake)
    print("\n🔄 PASO 2: Marcando migraciones como no aplicadas")
    for app in apps:
        if not ejecutar_comando(f"python manage.py migrate {app} zero --fake", f"Reset fake de {app}"):
            print(f"⚠️  Continuando con siguiente app...")
    
    # Paso 3: Aplicar migraciones iniciales como fake
    print("\n🔄 PASO 3: Aplicando migraciones iniciales como fake")
    for app in apps:
        if not ejecutar_comando(f"python manage.py migrate {app} --fake-initial", f"Fake initial de {app}"):
            print(f"⚠️  Continuando con siguiente app...")
    
    # Paso 4: Aplicar todas las migraciones restantes como fake
    print("\n🔄 PASO 4: Aplicando todas las migraciones como fake")
    if not ejecutar_comando("python manage.py migrate --fake", "Aplicar todas las migraciones como fake"):
        print("⚠️  Puede haber algunas migraciones que no se pudieron marcar como fake")
    
    # Paso 5: Verificar estado final
    print("\n📊 PASO 5: Verificando estado final")
    if not ejecutar_comando("python manage.py showmigrations", "Estado final de migraciones"):
        return False
    
    # Paso 6: Verificar que no hay migraciones pendientes
    print("\n🔍 PASO 6: Verificando migraciones pendientes")
    if not ejecutar_comando("python manage.py migrate --dry-run", "Verificar migraciones pendientes"):
        return False
    
    print("\n🎉 RESET DE MIGRACIONES COMPLETADO")
    print("=" * 60)
    print("✅ Todas las migraciones han sido marcadas como aplicadas")
    print("✅ No deberías tener más conflictos de columnas duplicadas")
    print("✅ Tu base de datos mantiene todos los datos existentes")
    
    return True

def main():
    """Función principal"""
    print("⚠️  IMPORTANTE: Este script debe ejecutarse en PythonAnywhere")
    print("⚠️  Asegúrate de haber hecho un respaldo de datos antes de continuar")
    
    respuesta = input("\n¿Continuar con el reset de migraciones? (s/N): ").lower().strip()
    
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Operación cancelada por el usuario")
        return
    
    if reset_migraciones():
        print("\n💡 PRÓXIMOS PASOS:")
        print("1. Reinicia tu aplicación web en PythonAnywhere")
        print("2. Verifica que todo funcione correctamente")
        print("3. Si hay problemas, restaura desde el respaldo")
    else:
        print("\n❌ El reset no se completó correctamente")
        print("💡 Revisa los errores y contacta soporte si es necesario")

if __name__ == "__main__":
    main()