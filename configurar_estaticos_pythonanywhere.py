#!/usr/bin/env python3
"""
Script para configurar archivos estáticos y media en PythonAnywhere
Optimizado para el flujo GitHub -> PythonAnywhere

Uso: python configurar_estaticos_pythonanywhere.py
"""

import os
import sys
import subprocess
from pathlib import Path

# Colores para output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def log(message, color=Colors.BLUE):
    """Función para logging con colores"""
    print(f"{color}[INFO]{Colors.NC} {message}")

def success(message):
    """Mensaje de éxito"""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def warning(message):
    """Mensaje de advertencia"""
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def error(message):
    """Mensaje de error"""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def run_command(command, description=""):
    """Ejecutar comando y manejar errores"""
    try:
        log(f"Ejecutando: {command}")
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        error(f"Error ejecutando {description}: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def main():
    """Función principal"""
    log("Iniciando configuración de archivos estáticos para PythonAnywhere...")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('manage.py'):
        error("No se encontró manage.py. Ejecuta este script desde el directorio raíz del proyecto.")
        sys.exit(1)
    
    project_dir = Path.cwd()
    log(f"Directorio del proyecto: {project_dir}")
    
    # ========================================
    # CONFIGURACIÓN DE DIRECTORIOS
    # ========================================
    
    # Crear directorios necesarios
    directories = [
        'static',
        'staticfiles',
        'media',
        'media/uploads',
        'media/qr_codes',
        'media/profile_pics'
    ]
    
    log("Creando directorios necesarios...")
    for directory in directories:
        dir_path = project_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        success(f"Directorio creado/verificado: {directory}")
    
    # ========================================
    # CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS
    # ========================================
    
    log("Configurando archivos estáticos...")
    
    # Verificar configuración de Django
    if not run_command("python manage.py check", "verificación de Django"):
        error("Error en la configuración de Django")
        return False
    
    # Recolectar archivos estáticos
    if not run_command("python manage.py collectstatic --noinput --clear", 
                      "recolección de archivos estáticos"):
        warning("Error recolectando archivos estáticos, intentando sin --clear")
        if not run_command("python manage.py collectstatic --noinput", 
                          "recolección de archivos estáticos (sin clear)"):
            error("No se pudieron recolectar los archivos estáticos")
            return False
    
    success("Archivos estáticos recolectados correctamente")
    
    # ========================================
    # VERIFICACIÓN DE PERMISOS
    # ========================================
    
    log("Verificando permisos de archivos...")
    
    # Verificar que los directorios tienen los permisos correctos
    for directory in ['static', 'staticfiles', 'media']:
        dir_path = project_dir / directory
        if dir_path.exists():
            # Establecer permisos 755 para directorios
            run_command(f"chmod 755 {dir_path}", f"permisos para {directory}")
            # Establecer permisos 644 para archivos dentro del directorio
            run_command(f"find {dir_path} -type f -exec chmod 644 {{}} \\;", 
                       f"permisos de archivos en {directory}")
    
    # ========================================
    # VERIFICACIÓN DE ARCHIVOS CRÍTICOS
    # ========================================
    
    log("Verificando archivos críticos...")
    
    critical_files = [
        'static/css/style.css',
        'static/js/main.js',
        'static/img/logo.png'
    ]
    
    for file_path in critical_files:
        full_path = project_dir / file_path
        if full_path.exists():
            success(f"Archivo encontrado: {file_path}")
        else:
            warning(f"Archivo no encontrado: {file_path}")
    
    # ========================================
    # INFORMACIÓN DE CONFIGURACIÓN
    # ========================================
    
    log("Generando información de configuración para PythonAnywhere...")
    
    staticfiles_dir = project_dir / 'staticfiles'
    media_dir = project_dir / 'media'
    
    print("\n" + "="*60)
    print("CONFIGURACIÓN PARA PANEL WEB DE PYTHONANYWHERE")
    print("="*60)
    print("\n📁 ARCHIVOS ESTÁTICOS:")
    print(f"   URL: /static/")
    print(f"   Directory: {staticfiles_dir}")
    
    print("\n📁 ARCHIVOS MEDIA:")
    print(f"   URL: /media/")
    print(f"   Directory: {media_dir}")
    
    print("\n🔧 CONFIGURACIÓN ADICIONAL:")
    print("   1. Ve al panel Web de PythonAnywhere")
    print("   2. En la sección 'Static files', agrega:")
    print(f"      - URL: /static/ → Directory: {staticfiles_dir}")
    print(f"      - URL: /media/ → Directory: {media_dir}")
    print("   3. Guarda los cambios")
    print("   4. Recarga tu aplicación web")
    
    # ========================================
    # ESTADÍSTICAS
    # ========================================
    
    log("Generando estadísticas...")
    
    # Contar archivos estáticos
    static_count = len(list(staticfiles_dir.rglob('*'))) if staticfiles_dir.exists() else 0
    media_count = len(list(media_dir.rglob('*'))) if media_dir.exists() else 0
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   Archivos estáticos: {static_count}")
    print(f"   Archivos media: {media_count}")
    
    # Tamaño de directorios
    try:
        static_size = subprocess.run(f"du -sh {staticfiles_dir}", shell=True, 
                                   capture_output=True, text=True)
        if static_size.returncode == 0:
            print(f"   Tamaño staticfiles: {static_size.stdout.split()[0]}")
    except:
        pass
    
    # ========================================
    # SCRIPT DE VERIFICACIÓN
    # ========================================
    
    verification_script = project_dir / 'verificar_estaticos.py'
    
    log("Creando script de verificación...")
    
    verification_code = '''#!/usr/bin/env python3
"""
Script de verificación de archivos estáticos
"""
import os
from pathlib import Path

def verificar_estaticos():
    """Verificar que los archivos estáticos están configurados correctamente"""
    project_dir = Path.cwd()
    
    print("🔍 Verificando configuración de archivos estáticos...")
    
    # Verificar directorios
    directories = ['static', 'staticfiles', 'media']
    for directory in directories:
        dir_path = project_dir / directory
        if dir_path.exists():
            count = len(list(dir_path.rglob('*')))
            print(f"✅ {directory}: {count} archivos")
        else:
            print(f"❌ {directory}: No existe")
    
    # Verificar archivos críticos
    critical_files = [
        'staticfiles/admin/css/base.css',
        'staticfiles/css/style.css',
        'static/css/style.css'
    ]
    
    print("\\n🔍 Verificando archivos críticos...")
    for file_path in critical_files:
        full_path = project_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")

if __name__ == "__main__":
    verificar_estaticos()
'''
    
    with open(verification_script, 'w', encoding='utf-8') as f:
        f.write(verification_code)
    
    # Hacer ejecutable
    run_command(f"chmod +x {verification_script}", "permisos del script de verificación")
    
    success(f"Script de verificación creado: {verification_script}")
    
    # ========================================
    # FINALIZACIÓN
    # ========================================
    
    print("\n" + "="*60)
    success("¡Configuración de archivos estáticos completada!")
    print("="*60)
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Configura las rutas en el panel Web de PythonAnywhere")
    print("2. Recarga tu aplicación web")
    print("3. Ejecuta 'python verificar_estaticos.py' para verificar")
    print("4. Prueba que CSS y JS cargan correctamente en tu sitio")
    
    print(f"\n🔗 URL de tu aplicación: https://tu_usuario.pythonanywhere.com")
    
    return True

if __name__ == "__main__":
    try:
        success_result = main()
        if success_result:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        warning("Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        error(f"Error inesperado: {e}")
        sys.exit(1)