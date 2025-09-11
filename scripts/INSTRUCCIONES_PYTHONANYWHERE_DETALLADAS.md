# Instrucciones Detalladas para Configurar la Tarea Programada en PythonAnywhere

## Introducción

Este documento proporciona instrucciones paso a paso para configurar la cancelación automática de reservas sin pago como una tarea programada en PythonAnywhere. El objetivo es ejecutar el comando Django de forma periódica para mantener el sistema de reservas limpio y eficiente.

## Requisitos Previos

- Cuenta en PythonAnywhere (gratuita o de pago)
- Proyecto de autolavados correctamente desplegado en PythonAnywhere
- Token de API de PythonAnywhere (para configuración automática)

## Opción 1: Configuración Manual

### Paso 1: Acceder a PythonAnywhere

1. Inicie sesión en su cuenta de PythonAnywhere en [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Navegue a la pestaña "Tasks" (Tareas) en el panel superior

### Paso 2: Crear una Nueva Tarea Programada

1. En la sección "Schedule" (Programar), seleccione la frecuencia deseada:
   - Para cuentas gratuitas: Seleccione "Daily" (Diario) y elija una hora
   - Para cuentas de pago: Seleccione "Every N minutes" (Cada N minutos) y elija 5 minutos

2. En el campo de comando, ingrese:
   ```bash
   cd ~/autolavados-plataforma && python manage.py cancelar_reservas_sin_pago
   ```

3. Haga clic en "Add task" (Agregar tarea) para crear la tarea programada

### Paso 3: Verificar la Configuración

1. La tarea aparecerá en la lista de tareas programadas
2. Puede hacer clic en "Run now" (Ejecutar ahora) para probar la tarea inmediatamente
3. Verifique los logs para asegurarse de que la tarea se ejecute sin errores

## Opción 2: Configuración Automática (Recomendado)

PythonAnywhere ofrece una API que permite configurar tareas programadas mediante programación. El proyecto incluye un script para automatizar este proceso.

### Paso 1: Obtener un Token de API

1. Inicie sesión en PythonAnywhere
2. Vaya a la página "Account" (Cuenta)
3. En la sección "API Token", haga clic en "Create a new API token" (Crear un nuevo token de API)
4. Copie el token generado

### Paso 2: Ejecutar el Script de Configuración

1. En su entorno local o en una consola de PythonAnywhere, ejecute:
   ```bash
   python configurar_tarea_pythonanywhere.py --username SU_USUARIO --token SU_TOKEN_API
   ```

2. Parámetros disponibles:
   - `--username`: Su nombre de usuario de PythonAnywhere (obligatorio)
   - `--token`: Su token de API de PythonAnywhere (obligatorio)
   - `--intervalo`: Intervalo en minutos para la ejecución (opcional, default: 5)
   - `--dry-run`: Ejecutar en modo simulación sin realizar cambios (opcional)

3. Ejemplo completo:
   ```bash
   python configurar_tarea_pythonanywhere.py --username MiUsuario --token a1b2c3d4e5f6g7h8i9j0 --intervalo 10
   ```

### Paso 3: Verificar la Configuración

1. El script mostrará un mensaje de confirmación si la tarea se configuró correctamente
2. Inicie sesión en PythonAnywhere y verifique que la tarea aparezca en la lista de tareas programadas

## Consideraciones para Cuentas Gratuitas

Las cuentas gratuitas de PythonAnywhere tienen limitaciones importantes:

1. **Frecuencia limitada**: Solo se permite programar tareas diarias, no cada pocos minutos
2. **Solución alternativa**: Configure la tarea para que se ejecute una vez al día y modifique el comando para ejecutar múltiples verificaciones:
   ```bash
   cd ~/autolavados-plataforma && for i in {1..10}; do python manage.py cancelar_reservas_sin_pago; sleep 300; done
   ```
   Este comando ejecutará la verificación 10 veces con un intervalo de 5 minutos (300 segundos) entre cada ejecución

## Registro y Monitoreo

### Habilitar Registro de Ejecución

1. Modifique el comando de la tarea para incluir redirección a un archivo de log:
   ```bash
   cd ~/autolavados-plataforma && python manage.py cancelar_reservas_sin_pago >> ~/logs/cancelaciones.log 2>&1
   ```

2. Para incluir la fecha y hora en cada entrada del log:
   ```bash
   cd ~/autolavados-plataforma && echo "[$(date)] Iniciando verificación" >> ~/logs/cancelaciones.log && python manage.py cancelar_reservas_sin_pago >> ~/logs/cancelaciones.log 2>&1
   ```

### Verificar los Logs

1. Acceda a la consola de PythonAnywhere
2. Ejecute el siguiente comando para ver los últimos registros:
   ```bash
   tail -n 50 ~/logs/cancelaciones.log
   ```

## Solución de Problemas

### La Tarea No Se Ejecuta

1. **Verificar permisos**: Asegúrese de que los archivos del proyecto tengan los permisos correctos
   ```bash
   chmod +x ~/autolavados-plataforma/manage.py
   ```

2. **Verificar entorno virtual**: Si usa un entorno virtual, modifique el comando:
   ```bash
   cd ~/autolavados-plataforma && source ~/.virtualenvs/myenv/bin/activate && python manage.py cancelar_reservas_sin_pago
   ```

3. **Verificar manualmente**: Ejecute el comando manualmente para ver si hay errores:
   ```bash
   cd ~/autolavados-plataforma && python manage.py cancelar_reservas_sin_pago --dry-run
   ```

### Error en la Configuración Automática

1. **Verificar token**: Asegúrese de que el token de API sea válido y esté activo
2. **Verificar permisos de API**: Confirme que su cuenta tenga permisos para usar la API de tareas
3. **Verificar conexión**: Asegúrese de tener conexión a Internet al ejecutar el script

## Personalización

### Cambiar el Tiempo de Espera

Para modificar el tiempo después del cual se cancelan las reservas sin pago:

1. Modifique el comando de la tarea para incluir el parámetro `--minutos`:
   ```bash
   cd ~/autolavados-plataforma && python manage.py cancelar_reservas_sin_pago --minutos=30
   ```

### Cambiar la Frecuencia de Ejecución

Para cuentas de pago, puede modificar la frecuencia de ejecución:

1. Vaya a la pestaña "Tasks" en PythonAnywhere
2. Elimine la tarea existente
3. Cree una nueva tarea con la frecuencia deseada

Alternativamente, use el script de configuración con el parámetro `--intervalo`:

```bash
python configurar_tarea_pythonanywhere.py --username SU_USUARIO --token SU_TOKEN_API --intervalo 10
```

## Contacto

Si tiene problemas con la configuración de la tarea programada en PythonAnywhere, contacte al administrador del sistema.