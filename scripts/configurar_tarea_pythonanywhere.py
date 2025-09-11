#!/usr/bin/env python
"""
Script para configurar automáticamente la tarea programada de cancelación de reservas sin pago en PythonAnywhere.

Este script utiliza la API de PythonAnywhere para crear o actualizar una tarea programada
que ejecuta periódicamente el comando de cancelación de reservas sin pago. Esto mantiene
el sistema limpio y libera horarios que no han sido pagados en el tiempo establecido.

Para usar este script:
1. Obtén un token de API de PythonAnywhere:
   - Inicia sesión en tu cuenta de PythonAnywhere
   - Ve a la página "Account" (Cuenta)
   - En la sección "API Token", haz clic en "Create a new API token"
   - Copia el token generado

2. Ejecuta el script con los parámetros requeridos:
   python configurar_tarea_pythonanywhere.py --username TU_USUARIO --token TU_TOKEN_API

3. Opciones adicionales:
   --intervalo=N    : Configura la ejecución cada N minutos (por defecto: 5)
   --dry-run        : Simula la configuración sin realizar cambios
   --comando=COMANDO: Especifica un comando personalizado (opcional)

Ejemplo completo:
   python configurar_tarea_pythonanywhere.py --username MiUsuario --token a1b2c3d4e5f6 --intervalo=10

Nota: Este script requiere el módulo 'requests'. Si no está instalado, ejecuta:
   pip install requests
"""

import argparse
import requests
import json
import sys

def configurar_tarea_programada(username, api_token, intervalo=5, dry_run=False, comando=None):
    """
    Configura una tarea programada en PythonAnywhere para ejecutar el comando de cancelación de reservas.
    
    Args:
        username (str): Nombre de usuario de PythonAnywhere
        api_token (str): Token de API de PythonAnywhere
        intervalo (int): Intervalo en minutos para la ejecución (por defecto: 5)
        dry_run (bool): Si es True, simula la configuración sin realizar cambios
        comando (str): Comando personalizado a ejecutar (opcional)
        
    Returns:
        bool: True si la operación fue exitosa, False en caso contrario
    """
    # URL de la API de PythonAnywhere para tareas programadas
    api_url = f"https://www.pythonanywhere.com/api/v0/user/{username}/schedule/"
    
    # Comando a ejecutar (usar el personalizado si se proporciona)
    if comando is None:
        comando = "cd ~/autolavados-plataforma && python manage.py cancelar_reservas_sin_pago"
    
    # Datos de la tarea programada
    task_data = {
        "command": comando,
        "enabled": True,
        "interval": "every_{}mins".format(intervalo),
        "hour": "*",
        "minute": "*/{}".format(intervalo),
        "description": "Cancelar reservas sin pago automáticamente"
    }
    
    # Cabeceras de la solicitud
    headers = {
        "Authorization": f"Token {api_token}",
        "Content-Type": "application/json"
    }
    
    # En modo simulación, solo mostrar lo que se haría
    if dry_run:
        print("\n📋 MODO SIMULACIÓN - No se realizarán cambios")
        print("\nSe configuraría la siguiente tarea programada:")
        print(f"  - Usuario: {username}")
        print(f"  - Comando: {comando}")
        print(f"  - Intervalo: Cada {intervalo} minutos")
        print(f"  - Descripción: {task_data['description']}")
        print("\nPara ejecutar realmente, elimine la opción --dry-run")
        return True
    
    try:
        # Realizar la solicitud POST para crear la tarea programada
        response = requests.post(api_url, headers=headers, data=json.dumps(task_data))
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 201:
            print("\n✅ Tarea programada creada exitosamente en PythonAnywhere")
            print(f"La tarea se ejecutará cada {intervalo} minutos")
            print(f"Comando configurado: {comando}")
            
            # Mostrar información de la respuesta
            task_info = response.json()
            if 'id' in task_info:
                print(f"ID de la tarea: {task_info['id']}")
            
            return True
        else:
            print(f"\n❌ Error al crear la tarea programada: {response.status_code}")
            print(f"Respuesta del servidor: {response.text}")
            
            # Sugerir soluciones comunes según el código de error
            if response.status_code == 401:
                print("\nPosible causa: Token de API inválido o expirado")
                print("Solución: Genera un nuevo token en la página de cuenta de PythonAnywhere")
            elif response.status_code == 403:
                print("\nPosible causa: No tienes permisos para crear tareas programadas")
                print("Solución: Verifica que tu cuenta tenga acceso a la API de tareas programadas")
            elif response.status_code == 400:
                print("\nPosible causa: Datos de la tarea inválidos")
                print("Solución: Verifica el formato del comando y el intervalo")
            
            return False
    except requests.exceptions.ConnectionError:
        print("\n❌ Error de conexión: No se pudo conectar con la API de PythonAnywhere")
        print("Verifica tu conexión a Internet y que la API de PythonAnywhere esté disponible")
        return False
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        return False

def main():
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(
        description="Configurar tarea programada en PythonAnywhere",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Ejemplos:
  Configuración básica:
    python configurar_tarea_pythonanywhere.py --username MiUsuario --token a1b2c3d4e5f6
  
  Configuración con intervalo personalizado:
    python configurar_tarea_pythonanywhere.py --username MiUsuario --token a1b2c3d4e5f6 --intervalo 10
  
  Simulación sin realizar cambios:
    python configurar_tarea_pythonanywhere.py --username MiUsuario --token a1b2c3d4e5f6 --dry-run
  
  Comando personalizado:
    python configurar_tarea_pythonanywhere.py --username MiUsuario --token a1b2c3d4e5f6 \
      --comando "cd ~/autolavados-plataforma && python manage.py verificar_reservas_vencidas"
"""
    )
    
    # Argumentos obligatorios
    parser.add_argument("--username", required=True, help="Nombre de usuario de PythonAnywhere")
    parser.add_argument("--token", required=True, help="Token de API de PythonAnywhere")
    
    # Argumentos opcionales
    parser.add_argument("--intervalo", type=int, default=5, help="Intervalo en minutos (por defecto: 5)")
    parser.add_argument("--dry-run", action="store_true", help="Simular la configuración sin realizar cambios")
    parser.add_argument("--comando", help="Comando personalizado a ejecutar (opcional)")
    
    # Parsear los argumentos
    args = parser.parse_args()
    
    # Validar argumentos
    if args.intervalo < 1:
        print("\n❌ Error: El intervalo debe ser al menos 1 minuto")
        sys.exit(1)
    
    # Mostrar banner
    print("\n" + "=" * 80)
    print("  CONFIGURADOR DE TAREAS PROGRAMADAS PARA PYTHONANYWHERE")
    print("=" * 80)
    
    # Configurar la tarea programada
    exito = configurar_tarea_programada(
        username=args.username,
        api_token=args.token,
        intervalo=args.intervalo,
        dry_run=args.dry_run,
        comando=args.comando
    )
    
    # Mensaje final
    if exito:
        if not args.dry_run:
            print("\n✨ Configuración completada exitosamente")
            print("Puedes verificar la tarea en: https://www.pythonanywhere.com/user/{}/schedule/".format(args.username))
    else:
        print("\n❌ La configuración no se completó debido a errores")
    
    # Salir con el código de estado apropiado
    sys.exit(0 if exito else 1)

if __name__ == "__main__":
    main()