# Cancelación Automática de Reservas Vencidas

## Descripción

Este sistema cancela automáticamente las reservas que han pasado su fecha y hora programada y siguen en estado PENDIENTE o CONFIRMADA. Esto ayuda a liberar horarios reservados y mantener el sistema actualizado.

## Archivos del Sistema

### Comando Django
- **Archivo:** `reservas/management/commands/cancelar_reservas_vencidas.py`
- **Uso:** `python manage.py cancelar_reservas_vencidas [--dry-run] [--horas=2]`

### Scripts de Windows
- **Script con ventana:** `scripts/cancelar_reservas_vencidas.bat`
- **Script silencioso:** `scripts/cancelar_reservas_vencidas_silencioso.vbs`

## Configuración de Tarea Programada en Windows

### Opción 1: Usando el Programador de Tareas (Recomendado)

1. **Abrir el Programador de Tareas:**
   - Presiona `Win + R`, escribe `taskschd.msc` y presiona Enter
   - O busca "Programador de tareas" en el menú de inicio

2. **Crear Nueva Tarea:**
   - Clic derecho en "Biblioteca del Programador de tareas"
   - Selecciona "Crear tarea básica..."

3. **Configurar la Tarea:**
   - **Nombre:** `Cancelar Reservas Vencidas CarWash`
   - **Descripción:** `Cancela automáticamente reservas vencidas cada 15 minutos`

4. **Configurar Desencadenador:**
   - Selecciona "Diariamente"
   - Hora de inicio: `00:00:00`
   - Repetir cada: `15 minutos`
   - Durante: `1 día`

5. **Configurar Acción:**
   - Selecciona "Iniciar un programa"
   - **Programa:** Ruta completa al script VBS silencioso:
     ```
     C:\Proyectos_2025\Proyecto_CarWash_Maicao\scripts\cancelar_reservas_vencidas_silencioso.vbs
     ```

6. **Configuraciones Adicionales:**
   - En la pestaña "General": Marcar "Ejecutar tanto si el usuario inició sesión como si no"
   - En la pestaña "Configuración": Marcar "Ejecutar la tarea tan pronto como sea posible después de un inicio programado perdido"

### Opción 2: Usando schtasks (Línea de comandos)

Ejecuta este comando en PowerShell como administrador:

```powershell
schtasks /create /tn "Cancelar Reservas Vencidas CarWash" /tr "C:\Proyectos_2025\Proyecto_CarWash_Maicao\scripts\cancelar_reservas_vencidas_silencioso.vbs" /sc minute /mo 15 /ru SYSTEM
```

## Configuración en Linux/macOS (Cron)

Edita el crontab:
```bash
crontab -e
```

Agrega esta línea:
```bash
# Cancelar reservas vencidas cada 15 minutos
*/15 * * * * cd /ruta/a/autolavados-plataforma && python manage.py cancelar_reservas_vencidas
```

## Configuración en PythonAnywhere

1. Ve a la pestaña "Tasks" en tu dashboard
2. Crea una nueva tarea programada
3. **Comando:** `cd ~/autolavados-plataforma && python manage.py cancelar_reservas_vencidas`
4. **Frecuencia:** Cada 15 minutos (si está disponible) o la más cercana

## Parámetros del Comando

### --dry-run
Ejecuta el comando en modo simulación sin realizar cambios reales:
```bash
python manage.py cancelar_reservas_vencidas --dry-run
```

### --horas
Especifica las horas de gracia después de la fecha programada (por defecto: 2):
```bash
python manage.py cancelar_reservas_vencidas --horas=1
```

## Verificación y Monitoreo

### Logs
Los scripts de Windows crean automáticamente logs en:
```
logs/cancelar_reservas_vencidas.log
```

### Verificación Manual
Ejecuta el comando con `--dry-run` para ver qué reservas serían canceladas:
```bash
python manage.py cancelar_reservas_vencidas --dry-run
```

### Base de Datos
Verifica en el panel de administración de Django que las reservas se estén cancelando correctamente.

## Solución de Problemas

### La tarea no se ejecuta
1. Verifica que la ruta del script sea correcta
2. Asegúrate de que Python esté en el PATH del sistema
3. Revisa los logs de Windows en el Visor de eventos

### Errores de permisos
1. Ejecuta el Programador de tareas como administrador
2. Configura la tarea para ejecutarse con privilegios de SYSTEM

### El comando falla
1. Verifica que el entorno virtual esté activado correctamente
2. Asegúrate de que todas las dependencias estén instaladas
3. Ejecuta el comando manualmente para identificar errores

## Beneficios del Sistema

- **Automatización completa:** No requiere intervención manual
- **Liberación de horarios:** Los horarios reservados se liberan automáticamente
- **Notificaciones:** Los clientes reciben notificaciones de cancelación
- **Mantenimiento del sistema:** Mantiene la base de datos limpia y actualizada
- **Flexibilidad:** Configurable con diferentes tiempos de gracia