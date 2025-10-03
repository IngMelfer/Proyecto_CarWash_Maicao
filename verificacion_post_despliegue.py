#!/usr/bin/env python3
"""
Script de verificación post-despliegue para PythonAnywhere
Verifica que todos los componentes del sistema funcionen correctamente

Uso: python verificacion_post_despliegue.py
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path
from datetime import datetime
import django
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings')

# Colores para output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def log(message, color=Colors.BLUE):
    """Función para logging con colores"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}]{Colors.NC} {message}")

def success(message):
    """Mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {message}{Colors.NC}")

def warning(message):
    """Mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")

def error(message):
    """Mensaje de error"""
    print(f"{Colors.RED}❌ {message}{Colors.NC}")

def info(message):
    """Mensaje informativo"""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.NC}")

class VerificadorDespliegue:
    def __init__(self):
        self.project_dir = Path.cwd()
        self.errores = []
        self.advertencias = []
        self.verificaciones_exitosas = 0
        self.total_verificaciones = 0
        
    def ejecutar_comando(self, comando, descripcion=""):
        """Ejecutar comando y capturar resultado"""
        try:
            resultado = subprocess.run(comando, shell=True, check=True,
                                     capture_output=True, text=True)
            return True, resultado.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    def verificar_estructura_proyecto(self):
        """Verificar que la estructura del proyecto sea correcta"""
        log("🔍 Verificando estructura del proyecto...", Colors.PURPLE)
        self.total_verificaciones += 1
        
        archivos_criticos = [
            'manage.py',
            'requirements.txt',
            'wsgi_pythonanywhere.py',
            '.env.pythonanywhere',
            'settings_production.py'
        ]
        
        directorios_criticos = [
            'autolavados_plataforma',
            'static',
            'staticfiles',
            'media'
        ]
        
        # Verificar archivos
        archivos_faltantes = []
        for archivo in archivos_criticos:
            if not (self.project_dir / archivo).exists():
                archivos_faltantes.append(archivo)
        
        if archivos_faltantes:
            self.errores.append(f"Archivos faltantes: {', '.join(archivos_faltantes)}")
            error(f"Archivos faltantes: {', '.join(archivos_faltantes)}")
        else:
            success("Todos los archivos críticos están presentes")
            self.verificaciones_exitosas += 1
        
        # Verificar directorios
        directorios_faltantes = []
        for directorio in directorios_criticos:
            if not (self.project_dir / directorio).exists():
                directorios_faltantes.append(directorio)
        
        if directorios_faltantes:
            self.advertencias.append(f"Directorios faltantes: {', '.join(directorios_faltantes)}")
            warning(f"Directorios faltantes: {', '.join(directorios_faltantes)}")
        else:
            success("Todos los directorios críticos están presentes")

    def verificar_dependencias(self):
        """Verificar que las dependencias estén instaladas"""
        log("📦 Verificando dependencias...", Colors.PURPLE)
        self.total_verificaciones += 1
        
        # Verificar pip freeze
        exito, salida = self.ejecutar_comando("pip freeze", "listado de paquetes")
        
        if not exito:
            self.errores.append("No se pudo obtener la lista de paquetes instalados")
            error("No se pudo obtener la lista de paquetes instalados")
            return
        
        paquetes_instalados = salida.lower()
        
        # Paquetes críticos
        paquetes_criticos = [
            'django',
            'mysqlclient',
            'python-dotenv',
            'qrcode',
            'pillow',
            'requests'
        ]
        
        paquetes_faltantes = []
        for paquete in paquetes_criticos:
            if paquete not in paquetes_instalados:
                paquetes_faltantes.append(paquete)
        
        if paquetes_faltantes:
            self.errores.append(f"Paquetes faltantes: {', '.join(paquetes_faltantes)}")
            error(f"Paquetes faltantes: {', '.join(paquetes_faltantes)}")
        else:
            success("Todas las dependencias críticas están instaladas")
            self.verificaciones_exitosas += 1

    def verificar_configuracion_django(self):
        """Verificar configuración de Django"""
        log("⚙️  Verificando configuración de Django...", Colors.PURPLE)
        self.total_verificaciones += 1
        
        # Verificar check de Django
        exito, salida = self.ejecutar_comando("python manage.py check", "verificación de Django")
        
        if not exito:
            self.errores.append(f"Error en configuración de Django: {salida}")
            error("Error en configuración de Django")
        else:
            success("Configuración de Django correcta")
            self.verificaciones_exitosas += 1

    def verificar_base_datos(self):
        """Verificar conexión y estado de la base de datos"""
        log("🗄️  Verificando base de datos...", Colors.PURPLE)
        self.total_verificaciones += 1
        
        try:
            # Configurar Django
            django.setup()
            from django.db import connection
            
            # Probar conexión
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                resultado = cursor.fetchone()
            
            if resultado:
                success("Conexión a base de datos exitosa")
                self.verificaciones_exitosas += 1
            else:
                self.errores.append("No se pudo conectar a la base de datos")
                error("No se pudo conectar a la base de datos")
                
        except Exception as e:
            self.errores.append(f"Error de base de datos: {str(e)}")
            error(f"Error de base de datos: {str(e)}")

    def verificar_migraciones(self):
        """Verificar estado de las migraciones"""
        log("🔄 Verificando migraciones...", Colors.PURPLE)
        self.total_verificaciones += 1
        
        # Verificar migraciones pendientes
        exito, salida = self.ejecutar_comando("python manage.py showmigrations --plan", 
                                            "estado de migraciones")
        
        if not exito:
            self.errores.append("No se pudo verificar el estado de las migraciones")
            error("No se pudo verificar el estado de las migraciones")
            return
        
        # Buscar migraciones no aplicadas
        lineas = salida.split('\n')
        migraciones_pendientes = [linea for linea in lineas if '[ ]' in linea]
        
        if migraciones_pendientes:
            self.advertencias.append(f"Migraciones pendientes: {len(migraciones_pendientes)}")
            warning(f"Hay {len(migraciones_pendientes)} migraciones pendientes")
            for migracion in migraciones_pendientes[:5]:  # Mostrar solo las primeras 5
                info(f"  {migracion.strip()}")
        else:
            success("Todas las migraciones están aplicadas")
            self.verificaciones_exitosas += 1

    def verificar_archivos_estaticos(self):
        """Verificar archivos estáticos"""
        log("🎨 Verificando archivos estáticos...", Colors.PURPLE)
        self.total_verificaciones += 1
        
        staticfiles_dir = self.project_dir / 'staticfiles'
        
        if not staticfiles_dir.exists():
            self.errores.append("Directorio staticfiles no existe")
            error("Directorio staticfiles no existe")
            return
        
        # Contar archivos estáticos
        archivos_estaticos = list(staticfiles_dir.rglob('*'))
        archivos_count = len([f for f in archivos_estaticos if f.is_file()])
        
        if archivos_count == 0:
            self.errores.append("No hay archivos estáticos recolectados")
            error("No hay archivos estáticos recolectados")
        else:
            success(f"Archivos estáticos encontrados: {archivos_count}")
            self.verificaciones_exitosas += 1
        
        # Verificar archivos críticos de admin
        admin_css = staticfiles_dir / 'admin' / 'css' / 'base.css'
        if admin_css.exists():
            success("Archivos estáticos de Django Admin encontrados")
        else:
            self.advertencias.append("Archivos estáticos de Django Admin no encontrados")
            warning("Archivos estáticos de Django Admin no encontrados")

    def verificar_variables_entorno(self):
        """Verificar variables de entorno"""
        log("🔐 Verificando variables de entorno...", Colors.PURPLE)
        self.total_verificaciones += 1
        
        variables_criticas = [
            'SECRET_KEY',
            'DEBUG',
            'ALLOWED_HOSTS',
            'DATABASE_NAME',
            'DATABASE_USER',
            'DATABASE_PASSWORD'
        ]
        
        variables_faltantes = []
        for variable in variables_criticas:
            if not os.getenv(variable):
                variables_faltantes.append(variable)
        
        if variables_faltantes:
            self.errores.append(f"Variables de entorno faltantes: {', '.join(variables_faltantes)}")
            error(f"Variables de entorno faltantes: {', '.join(variables_faltantes)}")
        else:
            success("Todas las variables de entorno críticas están configuradas")
            self.verificaciones_exitosas += 1

    def verificar_permisos(self):
        """Verificar permisos de archivos y directorios"""
        log("🔒 Verificando permisos...", Colors.PURPLE)
        self.total_verificaciones += 1
        
        directorios_verificar = ['media', 'staticfiles', 'static']
        problemas_permisos = []
        
        for directorio in directorios_verificar:
            dir_path = self.project_dir / directorio
            if dir_path.exists():
                if not os.access(dir_path, os.R_OK | os.W_OK):
                    problemas_permisos.append(directorio)
        
        if problemas_permisos:
            self.advertencias.append(f"Problemas de permisos en: {', '.join(problemas_permisos)}")
            warning(f"Problemas de permisos en: {', '.join(problemas_permisos)}")
        else:
            success("Permisos de directorios correctos")
            self.verificaciones_exitosas += 1

    def verificar_urls_principales(self):
        """Verificar que las URLs principales respondan"""
        log("🌐 Verificando URLs principales...", Colors.PURPLE)
        self.total_verificaciones += 1
        
        try:
            # Configurar Django para poder usar reverse
            django.setup()
            from django.urls import reverse
            from django.test import Client
            
            client = Client()
            
            # URLs a verificar
            urls_verificar = [
                '/',  # Página principal
                '/admin/',  # Admin
            ]
            
            urls_funcionando = 0
            for url in urls_verificar:
                try:
                    response = client.get(url)
                    if response.status_code in [200, 302, 301]:
                        urls_funcionando += 1
                        success(f"URL {url} responde correctamente ({response.status_code})")
                    else:
                        warning(f"URL {url} responde con código {response.status_code}")
                except Exception as e:
                    warning(f"Error verificando URL {url}: {str(e)}")
            
            if urls_funcionando == len(urls_verificar):
                self.verificaciones_exitosas += 1
            else:
                self.advertencias.append(f"Solo {urls_funcionando}/{len(urls_verificar)} URLs funcionan correctamente")
                
        except Exception as e:
            self.errores.append(f"Error verificando URLs: {str(e)}")
            error(f"Error verificando URLs: {str(e)}")

    def generar_reporte(self):
        """Generar reporte final"""
        print("\n" + "="*80)
        print("📊 REPORTE DE VERIFICACIÓN POST-DESPLIEGUE")
        print("="*80)
        
        # Estadísticas generales
        porcentaje_exito = (self.verificaciones_exitosas / self.total_verificaciones * 100) if self.total_verificaciones > 0 else 0

        print("\n📈 ESTADÍSTICAS:")
        print(f"   Verificaciones exitosas: {self.verificaciones_exitosas}/{self.total_verificaciones}")
        print(f"   Porcentaje de éxito: {porcentaje_exito:.1f}%")
        print(f"   Errores encontrados: {len(self.errores)}")
        print(f"   Advertencias: {len(self.advertencias)}")

        # Estado general
        if len(self.errores) == 0 and porcentaje_exito >= 80:
            print(f"\n{Colors.GREEN}🎉 ESTADO: DESPLIEGUE EXITOSO{Colors.NC}")
            print("   Tu aplicación está lista para producción!")
        elif len(self.errores) == 0:
            print(f"\n{Colors.YELLOW}⚠️  ESTADO: DESPLIEGUE CON ADVERTENCIAS{Colors.NC}")
            print("   Tu aplicación funciona pero hay mejoras pendientes")
        else:
            print(f"\n{Colors.RED}❌ ESTADO: DESPLIEGUE CON ERRORES{Colors.NC}")
            print("   Hay errores críticos que deben resolverse")

        # Errores
        if self.errores:
            print(f"\n{Colors.RED}🚨 ERRORES CRÍTICOS:{Colors.NC}")
            for i, err_msg in enumerate(self.errores, 1):
                print(f"   {i}. {err_msg}")

        # Advertencias
        if self.advertencias:
            print(f"\n{Colors.YELLOW}⚠️  ADVERTENCIAS:{Colors.NC}")
            for i, advertencia in enumerate(self.advertencias, 1):
                print(f"   {i}. {advertencia}")

        # Recomendaciones
        print("\n💡 RECOMENDACIONES:")
        if self.errores:
            print("   1. Resuelve los errores críticos antes de continuar")
            print("   2. Ejecuta este script nuevamente después de las correcciones")

        if self.advertencias:
            print("   3. Revisa las advertencias para optimizar el despliegue")

        print("   4. Verifica manualmente tu sitio web en el navegador")
        print("   5. Prueba las funcionalidades principales de tu aplicación")

        # Información adicional
        print("\n🔗 INFORMACIÓN ÚTIL:")
        print("   Panel Web PythonAnywhere: https://www.pythonanywhere.com/user/tu_usuario/webapps/")
        print("   Logs de errores: /var/log/tu_usuario.pythonanywhere.com.error.log")
        print("   Logs del servidor: /var/log/tu_usuario.pythonanywhere.com.server.log")

        return len(self.errores) == 0


def main():
    """Función principal"""
    print(Colors.CYAN)
    print("="*80)
    print("🚀 VERIFICACIÓN POST-DESPLIEGUE PYTHONANYWHERE")
    print("="*80)
    print(Colors.NC)
    
    verificador = VerificadorDespliegue()
    
    # Ejecutar todas las verificaciones
    verificaciones = [
        verificador.verificar_estructura_proyecto,
        verificador.verificar_dependencias,
        verificador.verificar_configuracion_django,
        verificador.verificar_base_datos,
        verificador.verificar_migraciones,
        verificador.verificar_archivos_estaticos,
        verificador.verificar_variables_entorno,
        verificador.verificar_permisos,
        verificador.verificar_urls_principales
    ]
    
    for verificacion in verificaciones:
        try:
            verificacion()
        except Exception as e:
            error(
                f"Error en verificación {verificacion.__name__}: {str(e)}"
            )
            verificador.errores.append(f"Error en {verificacion.__name__}: {str(e)}")
        print()  # Línea en blanco entre verificaciones
    
    # Generar reporte final
    exito = verificador.generar_reporte()
    
    # Guardar log
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"verificacion_despliegue_{timestamp}.log"
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"Verificación post-despliegue - {datetime.now()}\n")
        f.write(f"Verificaciones exitosas: {verificador.verificaciones_exitosas}/{verificador.total_verificaciones}\n")
        f.write(f"Errores: {len(verificador.errores)}\n")
        f.write(f"Advertencias: {len(verificador.advertencias)}\n\n")
        
        if verificador.errores:
            f.write("ERRORES:\n")
            for err_msg in verificador.errores:
                f.write(f"- {err_msg}\n")
            f.write("\n")
        
        if verificador.advertencias:
            f.write("ADVERTENCIAS:\n")
            for advertencia in verificador.advertencias:
                f.write(f"- {advertencia}\n")
    info(f"Log guardado en: {log_file}")

    return 0 if exito else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        warning("Verificación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        error(f"Error inesperado: {e}")
        sys.exit(1)