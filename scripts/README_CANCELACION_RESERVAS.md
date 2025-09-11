# Sistema de Cancelación Automática de Reservas Sin Pago

## Descripción General

El sistema de cancelación automática de reservas sin pago es un componente crítico de la plataforma de autolavados que permite liberar horarios y recursos cuando los clientes no completan el proceso de pago en un tiempo determinado. Esto mejora la eficiencia del negocio y evita bloqueos innecesarios de horarios disponibles.

## Componentes del Sistema

### 1. Comando Django

El núcleo del sistema es un comando Django personalizado que identifica y procesa las reservas pendientes sin pago:

```bash
python manage.py cancelar_reservas_sin_pago [--dry-run] [--minutos=15]
```

**Parámetros:**
- `--dry-run`: Ejecuta en modo simulación sin realizar cambios reales
- `--minutos`: Tiempo en minutos para considerar una reserva como abandonada (default: 15)

**Ubicación:** `reservas/management/commands/cancelar_reservas_sin_pago.py`

### 2. Scripts de Ejecución

Para facilitar la ejecución automática, se proporcionan dos scripts:

#### Script Batch (Windows)

**Archivo:** `cancelar_reservas_sin_pago.bat`

Ejecuta el comando Django redirigiendo la salida para minimizar la interacción con el usuario.

#### Script VBS (Ejecución Silenciosa en Windows)

**Archivo:** `cancelar_reservas_sin_pago_silencioso.vbs`

Ejecuta el comando Django de forma completamente silenciosa, sin mostrar ninguna ventana o interfaz gráfica. Ideal para tareas programadas.

### 3. Configuración para PythonAnywhere

**Archivo:** `configurar_tarea_pythonanywhere.py`

Script para configurar automáticamente la tarea programada en PythonAnywhere mediante su API.

```bash
python configurar_tarea_pythonanywhere.py --username TU_USUARIO --token TU_TOKEN_API [--intervalo=5]
```

## Configuración

### En Windows (Local o Servidor)

1. **Usando el Programador de Tareas:**
   - Abra el Programador de tareas de Windows
   - Cree una nueva tarea básica
   - Configure para ejecutar `cancelar_reservas_sin_pago_silencioso.vbs` cada 5 minutos
   - Asegúrese de que se ejecute con privilegios elevados

   Para instrucciones detalladas, consulte `INSTRUCCIONES_TAREA_PROGRAMADA.txt`

2. **Ejecución Manual (Pruebas):**
   ```
   cd C:\Proyectos_2025\autolavados-plataforma\scripts
   cscript cancelar_reservas_sin_pago_silencioso.vbs
   ```

### En PythonAnywhere

1. **Configuración Manual:**
   - Acceda a su cuenta de PythonAnywhere
   - Vaya a la pestaña "Tasks" (Tareas)
   - Cree una nueva tarea programada con la siguiente configuración:
     - Frecuencia: Cada 5 minutos
     - Comando: `cd ~/autolavados-plataforma && python manage.py cancelar_reservas_sin_pago`

2. **Configuración Automática:**
   ```bash
   python configurar_tarea_pythonanywhere.py --username TU_USUARIO --token TU_TOKEN_API
   ```

   Para instrucciones detalladas, consulte `INSTRUCCIONES_PYTHONANYWHERE.txt`

## Flujo de Trabajo

1. El script se ejecuta periódicamente (cada 5 minutos recomendado)
2. Identifica reservas pendientes creadas hace más del tiempo configurado (15 minutos por defecto)
3. Para cada reserva identificada:
   - Cambia su estado a CANCELADA
   - Actualiza las notas con información sobre la cancelación automática
   - Libera el horario reservado (decrementa contador en HorarioDisponible)
   - Crea una notificación para el cliente

## Consideraciones de Diseño

- **Ejecución Silenciosa:** Los scripts están diseñados para ejecutarse sin interacción del usuario
- **Configurabilidad:** El tiempo de espera es configurable mediante el parámetro `--minutos`
- **Modo Simulación:** El parámetro `--dry-run` permite probar sin realizar cambios reales
- **Notificaciones:** Se generan notificaciones automáticas para informar a los clientes
- **Liberación de Recursos:** Se liberan automáticamente los horarios reservados

## Mantenimiento y Solución de Problemas

### Verificación

Para verificar que el sistema está funcionando correctamente:

1. Cree manualmente una reserva de prueba
2. No realice el pago
3. Espere al menos 15 minutos
4. Verifique que la reserva haya sido cancelada automáticamente

### Logs

Para habilitar el registro de la ejecución:

- **En Windows:** Modifique el archivo VBS para escribir en un archivo de log:
  ```vbs
  objShell.Run "cmd /c echo Ejecutado en " & Now & " >> C:\Proyectos_2025\autolavados-plataforma\scripts\log_cancelaciones.txt", 0, True
  ```

- **En PythonAnywhere:** Modifique el comando para incluir redirección a un archivo de log:
  ```
  cd ~/autolavados-plataforma && python manage.py cancelar_reservas_sin_pago >> ~/logs/cancelaciones.log 2>&1
  ```

### Errores Comunes

1. **La tarea no se ejecuta:** Verifique los permisos y rutas
2. **Error de zona horaria:** Asegúrese de que la configuración de zona horaria sea correcta en Django
3. **Error de conexión a la base de datos:** Verifique las credenciales y la conexión

## Contacto

Si tiene problemas con la configuración del sistema de cancelación automática, contacte al administrador del sistema.