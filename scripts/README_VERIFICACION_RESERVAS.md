# Sistema de Verificación de Reservas Vencidas

## Descripción General

El sistema de verificación de reservas vencidas es un componente importante de la plataforma de autolavados que identifica y marca como incumplidas las reservas que ya pasaron su fecha y hora programada sin ser completadas. Esto permite mantener estadísticas precisas sobre el cumplimiento de citas y liberar recursos del sistema.

## Componentes del Sistema

### 1. Comando Django

El núcleo del sistema es un comando Django personalizado que identifica y procesa las reservas vencidas:

```bash
python manage.py verificar_reservas_vencidas [--dry-run]
```

**Parámetros:**
- `--dry-run`: Ejecuta en modo simulación sin realizar cambios reales

**Ubicación:** `reservas/management/commands/verificar_reservas_vencidas.py`

## Flujo de Trabajo

1. El script se ejecuta periódicamente (cada hora recomendado)
2. Identifica dos tipos de reservas vencidas:
   - Reservas de fechas anteriores al día actual
   - Reservas del día actual cuya hora ya pasó
3. Para cada reserva identificada:
   - Cambia su estado a INCUMPLIDA
   - Actualiza las notas con información sobre el cambio automático
   - Crea una notificación para el cliente

## Configuración

### En Windows (Local o Servidor)

1. **Usando el Programador de Tareas:**
   - Abra el Programador de tareas de Windows
   - Cree una nueva tarea básica
   - Configure para ejecutar el comando cada hora
   - Ejemplo de comando:
     ```
     cmd /c cd C:\Proyectos_2025\autolavados-plataforma && python manage.py verificar_reservas_vencidas
     ```

### En PythonAnywhere

1. **Configuración Manual:**
   - Acceda a su cuenta de PythonAnywhere
   - Vaya a la pestaña "Tasks" (Tareas)
   - Cree una nueva tarea programada con la siguiente configuración:
     - Frecuencia: Cada hora
     - Comando: `cd ~/autolavados-plataforma && python manage.py verificar_reservas_vencidas`

2. **Configuración Automática:**
   ```bash
   python configurar_tarea_pythonanywhere.py --username TU_USUARIO --token TU_TOKEN_API \
     --intervalo 60 --comando "cd ~/autolavados-plataforma && python manage.py verificar_reservas_vencidas"
   ```

### En Linux (Producción)

**Usando Cron:**

1. Abra el archivo crontab:
   ```bash
   crontab -e
   ```

2. Agregue la siguiente entrada:
   ```
   # Verificar reservas vencidas cada hora
   0 * * * * cd /ruta/a/autolavados-plataforma && python manage.py verificar_reservas_vencidas
   ```

## Consideraciones de Diseño

- **Ejecución Periódica:** El sistema está diseñado para ejecutarse periódicamente (cada hora recomendado)
- **Modo Simulación:** El parámetro `--dry-run` permite probar sin realizar cambios reales
- **Notificaciones:** Se generan notificaciones automáticas para informar a los clientes
- **Criterios de Vencimiento:** Se consideran dos criterios para determinar si una reserva está vencida:
  1. La fecha de la reserva es anterior a la fecha actual
  2. La fecha es la actual pero la hora ya pasó

## Mantenimiento y Solución de Problemas

### Verificación

Para verificar que el sistema está funcionando correctamente:

1. Cree manualmente una reserva de prueba con fecha y hora pasadas
2. Ejecute el comando manualmente:
   ```bash
   python manage.py verificar_reservas_vencidas --dry-run
   ```
3. Verifique que la reserva aparezca en la lista de reservas a marcar como incumplidas
4. Ejecute el comando sin `--dry-run` y verifique que la reserva haya sido marcada como incumplida

### Logs

Para habilitar el registro de la ejecución:

- **En Windows:** Redirija la salida a un archivo de log:
  ```
  cmd /c cd C:\Proyectos_2025\autolavados-plataforma && python manage.py verificar_reservas_vencidas >> C:\Proyectos_2025\autolavados-plataforma\logs\verificacion.log 2>&1
  ```

- **En PythonAnywhere:** Modifique el comando para incluir redirección a un archivo de log:
  ```
  cd ~/autolavados-plataforma && python manage.py verificar_reservas_vencidas >> ~/logs/verificacion.log 2>&1
  ```

### Errores Comunes

1. **La tarea no se ejecuta:** Verifique los permisos y rutas
2. **Error de zona horaria:** Asegúrese de que la configuración de zona horaria sea correcta en Django
3. **Error de conexión a la base de datos:** Verifique las credenciales y la conexión

## Diferencias con el Sistema de Cancelación de Reservas Sin Pago

Es importante entender la diferencia entre los dos sistemas automáticos:

1. **Cancelación de Reservas Sin Pago:**
   - Cancela reservas PENDIENTES que no han sido pagadas después de un tiempo determinado
   - Se ejecuta cada 5 minutos
   - Libera horarios para que otros clientes puedan reservar

2. **Verificación de Reservas Vencidas:**
   - Marca como INCUMPLIDAS las reservas PENDIENTES o CONFIRMADAS cuya fecha y hora ya pasaron
   - Se ejecuta cada hora
   - Mantiene estadísticas precisas sobre el cumplimiento de citas

## Contacto

Si tiene problemas con la configuración del sistema de verificación de reservas vencidas, contacte al administrador del sistema.