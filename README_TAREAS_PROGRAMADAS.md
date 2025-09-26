# Tareas Programadas del Sistema

## Introducción

Este documento describe las tareas programadas implementadas en el sistema de autolavados, su propósito, configuración y mantenimiento. Las tareas programadas son procesos automatizados que se ejecutan periódicamente para mantener el sistema funcionando correctamente sin intervención manual.

## Tareas Programadas Disponibles

### 1. Cancelación de Reservas Sin Pago

**Propósito:** Cancelar automáticamente las reservas que permanecen en estado PENDIENTE sin completar el pago después de un tiempo determinado (5 minutos por defecto).

**Comando Django:** `python manage.py cancelar_reservas_sin_pago [--dry-run] [--minutos=5]`

**Archivos relacionados:**
- Comando: `reservas/management/commands/cancelar_reservas_sin_pago.py`
- Script Windows: `scripts/cancelar_reservas_sin_pago.bat`
- Script silencioso Windows: `scripts/cancelar_reservas_sin_pago_silencioso.vbs`
- Documentación detallada: `scripts/README_CANCELACION_RESERVAS.md`

**Frecuencia recomendada:** Cada 5 minutos

**Documentación detallada:**
- [Instrucciones para Windows](scripts/INSTRUCCIONES_TAREA_PROGRAMADA_DETALLADAS.md)
- [Instrucciones para PythonAnywhere](scripts/INSTRUCCIONES_PYTHONANYWHERE_DETALLADAS.md)

### 2. Cancelación de Reservas Vencidas

**Propósito:** Cancelar automáticamente las reservas que han pasado su fecha y hora programada y siguen en estado PENDIENTE o CONFIRMADA, liberando los horarios reservados.

**Comando Django:** `python manage.py cancelar_reservas_vencidas [--dry-run] [--horas=2]`

**Archivos relacionados:**
- Comando: `reservas/management/commands/cancelar_reservas_vencidas.py`

**Frecuencia recomendada:** Cada 15 minutos

### 3. Verificación de Reservas Vencidas

**Propósito:** Identificar y marcar como INCUMPLIDAS las reservas que ya pasaron su fecha y hora programada y no fueron completadas.

**Comando Django:** `python manage.py verificar_reservas_vencidas [--dry-run]`

**Archivos relacionados:**
- Comando: `reservas/management/commands/verificar_reservas_vencidas.py`

**Frecuencia recomendada:** Cada hora

## Configuración en Diferentes Entornos

### Windows (Desarrollo o Producción)

#### Usando el Programador de Tareas

1. Abra el Programador de tareas de Windows
2. Cree una nueva tarea básica
3. Configure la frecuencia de ejecución según la tarea
4. Seleccione el script correspondiente:
   - Para ejecución silenciosa: `cancelar_reservas_sin_pago_silencioso.vbs`
   - Para ejecución con ventana: `cancelar_reservas_sin_pago.bat`

Consulte [Instrucciones detalladas para Windows](scripts/INSTRUCCIONES_TAREA_PROGRAMADA_DETALLADAS.md) para más información.

### PythonAnywhere (Producción)

#### Configuración Manual

1. Acceda a la pestaña "Tasks" en PythonAnywhere
2. Cree una nueva tarea programada con la frecuencia deseada
3. Ingrese el comando correspondiente:
   ```bash
   cd ~/autolavados-plataforma && python manage.py cancelar_reservas_sin_pago
   ```

#### Configuración Automática

Utilice el script proporcionado para configurar automáticamente las tareas:

```bash
python configurar_tarea_pythonanywhere.py --username SU_USUARIO --token SU_TOKEN_API
```

Consulte [Instrucciones detalladas para PythonAnywhere](scripts/INSTRUCCIONES_PYTHONANYWHERE_DETALLADAS.md) para más información.

### Linux (Producción)

#### Usando Cron

1. Abra el archivo crontab:
   ```bash
   crontab -e
   ```

2. Agregue las entradas correspondientes:
   ```
   # Cancelar reservas sin pago cada 5 minutos
   */5 * * * * cd /ruta/a/autolavados-plataforma && python manage.py cancelar_reservas_sin_pago
   
   # Cancelar reservas vencidas cada 15 minutos
   */15 * * * * cd /ruta/a/autolavados-plataforma && python manage.py cancelar_reservas_vencidas
   
   # Verificar reservas vencidas cada hora
   0 * * * * cd /ruta/a/autolavados-plataforma && python manage.py verificar_reservas_vencidas
   ```

## Verificación y Solución de Problemas

### Verificación de Funcionamiento

1. **Prueba manual:** Ejecute el comando con la opción `--dry-run` para simular la ejecución sin realizar cambios
2. **Verificación en base de datos:** Compruebe que las reservas se estén cancelando o marcando como incumplidas según corresponda
3. **Logs:** Revise los archivos de registro si ha configurado la redirección de salida

### Problemas Comunes

1. **La tarea no se ejecuta:**
   - Verifique permisos y rutas
   - Asegúrese de que Python esté en el PATH del sistema o especifique la ruta completa
   - Compruebe que el entorno virtual esté activado si corresponde

2. **Errores en la ejecución:**
   - Revise los logs para identificar el problema
   - Ejecute manualmente el comando para ver los mensajes de error
   - Verifique la conexión a la base de datos

## Personalización

### Modificar Tiempo de Espera

Para cambiar el tiempo después del cual se cancelan las reservas sin pago:

1. Edite el script correspondiente y agregue el parámetro `--minutos`:
   ```
   python manage.py cancelar_reservas_sin_pago --minutos=30
   ```

### Cambiar Frecuencia de Ejecución

Modifique la configuración de la tarea programada según el entorno:
- Windows: Edite la tarea en el Programador de tareas
- PythonAnywhere: Modifique la tarea en la pestaña "Tasks"
- Linux: Edite el archivo crontab

## Seguridad y Consideraciones

1. **Permisos:** Asegúrese de que las tareas se ejecuten con los permisos adecuados
2. **Logs:** Configure la redirección de salida para facilitar la depuración
3. **Notificaciones:** Las tareas generan notificaciones automáticas para los clientes afectados
4. **Respaldo:** Realice copias de seguridad regulares de la base de datos

## Contacto

Si tiene problemas con la configuración o ejecución de las tareas programadas, contacte al administrador del sistema.