# Configuración de Tareas Programadas

Este documento describe cómo configurar las tareas programadas necesarias para el funcionamiento automático de la plataforma de autolavados.

## Tareas Programadas Requeridas

### 1. Cancelación de Reservas Sin Pago

Esta tarea cancela automáticamente las reservas que no han sido pagadas después de un tiempo determinado.

- **Script**: `scripts\ejecutar_cancelacion_reservas.vbs`
- **Frecuencia recomendada**: Cada 15 minutos
- **Comando Django**: `python manage.py cancelar_reservas_sin_pago`

### 2. Gestión Automática de Servicios

Esta tarea gestiona automáticamente el inicio y finalización de servicios:
- Inicia servicios confirmados 5 minutos después de la hora programada si el administrador no lo ha hecho
- Finaliza servicios en proceso después de 10 minutos de iniciado el servicio

- **Script**: `scripts\ejecutar_gestion_servicios.vbs`
- **Frecuencia recomendada**: Cada 5 minutos
- **Comando Django**: `python manage.py gestionar_servicios_automaticos`

## Configuración en Windows

### Usando el Programador de Tareas de Windows

1. Abrir el Programador de Tareas de Windows (buscar "Programador de tareas" en el menú Inicio)
2. Hacer clic en "Crear tarea básica" en el panel derecho
3. Seguir el asistente:
   - Nombre: "Autolavados - Cancelación de Reservas" o "Autolavados - Gestión de Servicios"
   - Descripción: Breve descripción de la tarea
   - Desencadenador: Diario
   - Hora de inicio: Cualquier hora
   - Repetir tarea cada: 15 minutos (para cancelación) o 5 minutos (para gestión de servicios)
   - Acción: Iniciar un programa
   - Programa/script: Ruta completa al archivo VBS correspondiente
     - Ejemplo: `C:\Proyectos_2025\autolavados-plataforma\scripts\ejecutar_gestion_servicios.vbs`
   - Finalizar el asistente

4. Después de crear la tarea, hacer clic derecho sobre ella y seleccionar "Propiedades"
5. En la pestaña "General", marcar:
   - "Ejecutar con privilegios más altos"
   - "Ejecutar independientemente de si el usuario tiene iniciada la sesión"
   - "No almacenar contraseña"
6. En la pestaña "Configuración", marcar:
   - "Permitir que la tarea se ejecute a petición"
   - "Si la tarea ya se está ejecutando, se aplica la siguiente regla: No iniciar una nueva instancia"
7. Hacer clic en "Aceptar" para guardar los cambios

### Verificación

Para verificar que las tareas programadas están funcionando correctamente:

1. Revisar los archivos de registro en la carpeta `scripts\logs`
2. Verificar en la base de datos que las reservas se están cancelando o los servicios se están iniciando/finalizando automáticamente según corresponda

## Configuración en PythonAnywhere (Entorno de Producción)

Si el sistema está desplegado en PythonAnywhere, se deben configurar tareas programadas usando la interfaz de PythonAnywhere:

1. Ir a la pestaña "Tasks" en el dashboard de PythonAnywhere
2. Agregar una nueva tarea programada con la frecuencia deseada
3. Comando para cancelación de reservas:
   ```
   cd /home/usuario/autolavados-plataforma && python manage.py cancelar_reservas_sin_pago
   ```
4. Comando para gestión de servicios:
   ```
   cd /home/usuario/autolavados-plataforma && python manage.py gestionar_servicios_automaticos
   ```

## Solución de Problemas

Si las tareas programadas no se están ejecutando correctamente:

1. Verificar que los scripts tengan permisos de ejecución
2. Comprobar que las rutas en los scripts sean correctas
3. Revisar los archivos de registro en busca de errores
4. Ejecutar los comandos manualmente para verificar que funcionan correctamente
5. Verificar que el entorno virtual de Python esté correctamente configurado y activado en los scripts