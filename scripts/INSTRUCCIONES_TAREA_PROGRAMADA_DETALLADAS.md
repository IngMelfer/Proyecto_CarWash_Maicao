# Instrucciones Detalladas para Configurar la Tarea Programada en Windows

## Introducción

Este documento proporciona instrucciones paso a paso para configurar la cancelación automática de reservas sin pago como una tarea programada en Windows. El objetivo es ejecutar el script de forma periódica y completamente silenciosa (sin mostrar ventanas de terminal).

## Requisitos Previos

- Windows 10 o superior
- Python instalado y configurado en el PATH del sistema
- Proyecto de autolavados correctamente configurado
- Permisos de administrador para configurar tareas programadas

## Opción 1: Usar el Programador de Tareas de Windows (Recomendado)

### Paso 1: Abrir el Programador de Tareas

1. Presione `Win + R` para abrir el cuadro de diálogo Ejecutar
2. Escriba `taskschd.msc` y presione Enter
3. Alternativamente, busque "Programador de tareas" en el menú Inicio

### Paso 2: Crear una Nueva Tarea

1. En el panel derecho, haga clic en "Crear tarea básica"
2. Complete la información básica:
   - **Nombre**: `CancelarReservasSinPago`
   - **Descripción**: `Cancela automáticamente las reservas pendientes sin pago después de 15 minutos`
   - Haga clic en "Siguiente"

### Paso 3: Configurar el Desencadenador

1. Seleccione "Diariamente" y haga clic en "Siguiente"
2. Configure la hora de inicio (cualquier hora es válida)
3. Haga clic en "Siguiente"
4. En la pantalla de configuración avanzada:
   - Marque "Repetir tarea cada:" y seleccione `5 minutos` en el menú desplegable
   - En "durante:" seleccione "Indefinidamente"
   - Haga clic en "Siguiente"

### Paso 4: Configurar la Acción

1. Seleccione "Iniciar un programa" y haga clic en "Siguiente"
2. En "Programa/script", haga clic en "Examinar" y navegue hasta:
   `C:\Proyectos_2025\autolavados-plataforma\scripts\cancelar_reservas_sin_pago_silencioso.vbs`
3. Deje los campos "Agregar argumentos" y "Iniciar en" vacíos
4. Haga clic en "Siguiente"

### Paso 5: Finalizar la Configuración

1. Revise el resumen y haga clic en "Finalizar"
2. Localice la tarea recién creada en la lista de tareas programadas
3. Haga clic derecho en la tarea y seleccione "Propiedades"

### Paso 6: Configuración Adicional (Importante)

1. En la pestaña "General":
   - Marque la opción "Ejecutar con privilegios más altos"
   - En "Configurar para:", seleccione su versión de Windows

2. En la pestaña "Condiciones":
   - Desmarque "Iniciar la tarea solo si el equipo está conectado a la alimentación de CA"
   - Desmarque otras condiciones restrictivas según sea necesario

3. En la pestaña "Configuración":
   - Marque "Ejecutar la tarea lo antes posible después de no iniciarse en la programación"
   - Marque "Si la tarea ya se está ejecutando, se aplica la siguiente regla:" y seleccione "No iniciar una nueva instancia"

4. Haga clic en "Aceptar" para guardar los cambios

## Opción 2: Usar el Archivo VBS Directamente

Si prefiere no usar el Programador de tareas, puede configurar el script para que se ejecute al iniciar sesión:

### Paso 1: Crear un Acceso Directo

1. Haga clic derecho en el escritorio o en la carpeta de inicio y seleccione "Nuevo" > "Acceso directo"
2. En la ubicación del elemento, escriba o navegue hasta:
   `C:\Proyectos_2025\autolavados-plataforma\scripts\cancelar_reservas_sin_pago_silencioso.vbs`
3. Haga clic en "Siguiente"
4. Asigne un nombre al acceso directo (por ejemplo, "Cancelar Reservas Sin Pago")
5. Haga clic en "Finalizar"

### Paso 2: Mover el Acceso Directo a la Carpeta de Inicio

1. Corte el acceso directo creado
2. Presione `Win + R`, escriba `shell:startup` y presione Enter
3. Pegue el acceso directo en esta carpeta

**Nota**: Esta opción ejecutará el script solo una vez al iniciar sesión, lo cual no es ideal para la cancelación periódica de reservas.

## Verificación

Para verificar que la tarea se está ejecutando correctamente:

### Método 1: Verificar en la Base de Datos

1. Cree manualmente una reserva de prueba
2. No realice el pago
3. Espere al menos 15 minutos
4. Verifique en la base de datos o en la interfaz de administración que la reserva haya sido cancelada

### Método 2: Habilitar Registro de Ejecución

1. Edite el archivo `cancelar_reservas_sin_pago_silencioso.vbs`
2. Antes de la línea `Set objShell = Nothing`, agregue:
   ```vbs
   objShell.Run "cmd /c echo Ejecutado en " & Now & " >> C:\Proyectos_2025\autolavados-plataforma\scripts\log_cancelaciones.txt", 0, True
   ```
3. Guarde el archivo
4. Después de que la tarea se ejecute, verifique el archivo `log_cancelaciones.txt` para confirmar la ejecución

## Solución de Problemas

### La Tarea No Se Ejecuta

1. **Verificar permisos**: Asegúrese de que la tarea se ejecute con privilegios de administrador
2. **Verificar rutas**: Confirme que las rutas en el script VBS sean correctas
3. **Verificar Python**: Asegúrese de que Python esté en el PATH del sistema o especifique la ruta completa en el script VBS

### Error en la Ejecución

1. **Habilitar visualización**: Modifique el valor `0` en `objShell.Run` a `1` en el script VBS para ver la ventana de ejecución y posibles errores
2. **Verificar manualmente**: Ejecute el script manualmente para ver si hay errores:
   ```
   cd C:\Proyectos_2025\autolavados-plataforma
   python manage.py cancelar_reservas_sin_pago --dry-run
   ```

## Personalización

### Cambiar el Tiempo de Espera

Para modificar el tiempo después del cual se cancelan las reservas sin pago:

1. Edite el archivo `cancelar_reservas_sin_pago_silencioso.vbs`
2. Modifique la línea que define `strCommand` para incluir el parámetro `--minutos`:
   ```vbs
   strCommand = "python C:\Proyectos_2025\autolavados-plataforma\manage.py cancelar_reservas_sin_pago --minutos=30"
   ```
3. Guarde el archivo

### Cambiar la Frecuencia de Ejecución

Para modificar cada cuánto tiempo se ejecuta la tarea:

1. Abra el Programador de tareas
2. Localice y haga clic derecho en la tarea "CancelarReservasSinPago"
3. Seleccione "Propiedades"
4. Vaya a la pestaña "Desencadenadores" y haga clic en "Editar"
5. Modifique el valor en "Repetir tarea cada:" (por ejemplo, 10 minutos en lugar de 5)
6. Haga clic en "Aceptar" para guardar los cambios

## Contacto

Si tiene problemas con la configuración de la tarea programada, contacte al administrador del sistema.