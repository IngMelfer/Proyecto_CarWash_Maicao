# Configuración de Tareas Programadas para Autolavados

Este documento explica cómo configurar las tareas programadas para el sistema de autolavados, específicamente la cancelación automática de reservas sin pago.

## Opciones de Despliegue

### 1. Despliegue en PythonAnywhere

Si el sistema está desplegado en PythonAnywhere, sigue estas instrucciones:

#### Configuración Manual

1. Accede a tu cuenta de PythonAnywhere
2. Ve a la pestaña "Tasks" (Tareas)
3. Crea una nueva tarea programada con la siguiente configuración:
   - Frecuencia: Cada 5 minutos
   - Comando: `cd ~/autolavados-plataforma && python manage.py cancelar_reservas_sin_pago`

#### Configuración Automática

Puedes usar el script `configurar_tarea_pythonanywhere.py` para configurar automáticamente la tarea:

```bash
python configurar_tarea_pythonanywhere.py --username TU_USUARIO --token TU_TOKEN_API
```

Para obtener un token de API:
1. Inicia sesión en PythonAnywhere
2. Ve a la página "Account" (Cuenta)
3. En la sección "API Token", genera un nuevo token

### 2. Despliegue en Windows (Local o Servidor)

Si el sistema está desplegado en un servidor Windows, tienes dos opciones:

#### Opción 1: Usar el Programador de Tareas de Windows

Configura una tarea programada para ejecutar el script VBS que hemos creado:

1. Abre el Programador de tareas de Windows
2. Crea una nueva tarea básica
3. Configúrala para ejecutar `cancelar_reservas_sin_pago_silencioso.vbs` cada 5 minutos
4. Asegúrate de que se ejecute de forma oculta

Consulta el archivo `INSTRUCCIONES_TAREA_PROGRAMADA.txt` para instrucciones detalladas.

#### Opción 2: Usar un Servicio de Windows

Para una solución más robusta, puedes crear un servicio de Windows:

1. Instala NSSM (Non-Sucking Service Manager)
2. Configura un servicio que ejecute un script que llame periódicamente al comando de Django

### 3. Despliegue en Linux/Unix

Si el sistema está desplegado en un servidor Linux:

```bash
# Editar el crontab
crontab -e

# Añadir esta línea para ejecutar cada 5 minutos
*/5 * * * * cd /ruta/a/autolavados-plataforma && python manage.py cancelar_reservas_sin_pago
```

## Verificación

Para verificar que la tarea programada está funcionando correctamente:

1. Crea manualmente una reserva de prueba
2. No realices el pago
3. Espera al menos 15 minutos
4. Verifica que la reserva haya sido cancelada automáticamente

## Solución de Problemas

### Logs

Para habilitar el registro de la ejecución:

- En PythonAnywhere: Modifica el comando para incluir `>> ~/logs/cancelaciones.log 2>&1`
- En Windows: Modifica el archivo VBS para escribir en un archivo de log
- En Linux: Añade redirección a un archivo de log en el crontab

### Errores Comunes

1. **La tarea no se ejecuta**: Verifica los permisos y rutas
2. **Error de zona horaria**: Asegúrate de que la configuración de zona horaria sea correcta en Django
3. **Error de conexión a la base de datos**: Verifica las credenciales y la conexión

## Personalización

Puedes modificar el comportamiento de la cancelación automática:

1. Cambia el tiempo de espera (por defecto 15 minutos) usando el parámetro `--minutos`:
   ```
   python manage.py cancelar_reservas_sin_pago --minutos 30
   ```

2. Ejecuta en modo simulación para probar sin realizar cambios:
   ```
   python manage.py cancelar_reservas_sin_pago --dry-run
   ```

## Contacto

Si tienes problemas con la configuración de las tareas programadas, contacta al administrador del sistema.