# Plataforma Integral para Autolavados - Premium Car Detailing

## Descripción General

Este proyecto implementa una plataforma completa para la gestión de autolavados, permitiendo a los clientes reservar servicios, recibir notificaciones y acumular puntos de fidelización. Para los administradores, ofrece herramientas de gestión de reservas, servicios, horarios y clientes.

## Características Principales

- **Sistema de Reservas**: Creación, confirmación y cancelación automática de reservas
- **Gestión de Horarios**: Administración de horarios disponibles para servicios
- **Gestión de Clientes**: Registro y administración de clientes y sus vehículos
- **Sistema de Notificaciones**: Notificaciones automáticas para clientes y administradores
- **API REST**: Interfaz completa para integración con aplicaciones móviles o de terceros
- **Panel de Administración**: Panel personalizado para gestión del negocio
- **Sistema de Fidelización**: Acumulación de puntos y beneficios para clientes frecuentes
- **Procesos Automáticos**: Cancelación de reservas sin pago y verificación de reservas vencidas

## Configuración del Proyecto

### Requisitos

- Python 3.10+
- PostgreSQL (producción) o SQLite (desarrollo)
- Pip
- Visual Studio Code (recomendado)

### Instalación

1. Clonar el repositorio

```bash
git clone https://github.com/IngMelfer/Proyecto_CarWash_Maicao.git
cd Proyecto_CarWash_Maicao
```

2. Crear y activar entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Instalar dependencias

```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar el archivo .env con tus configuraciones
5. Ejecutar migraciones

```bash
python manage.py migrate
```

6. Crear superusuario (opcional)

```bash
python manage.py createsuperuser
```

7. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

### Configuración en Visual Studio Code

1. Abrir el proyecto en Visual Studio Code

2. Instalar la extensión de Python para VS Code

3. Seleccionar el intérprete de Python del entorno virtual:
   - Presiona `Ctrl+Shift+P`
   - Escribe "Python: Select Interpreter"
   - Selecciona el intérprete de la carpeta `venv`

4. Para solucionar problemas comunes:

   - Si aparece error de PyMySQL, asegúrate de instalarlo:
     ```bash
     pip install PyMySQL==1.1.0
     ```

   - Si aparece error de psycopg2, instala la versión binaria:
     ```bash
     pip install psycopg2-binary==2.9.9
     ```

## Tareas Programadas

El sistema incluye dos procesos automáticos importantes:

1. **Cancelación de Reservas Sin Pago**: Cancela automáticamente las reservas que no han sido pagadas después de un tiempo determinado.
   - [Documentación detallada](scripts/README_CANCELACION_RESERVAS.md)
   - [Instrucciones para Windows](scripts/INSTRUCCIONES_TAREA_PROGRAMADA_DETALLADAS.md)
   - [Instrucciones para PythonAnywhere](scripts/INSTRUCCIONES_PYTHONANYWHERE_DETALLADAS.md)

2. **Verificación de Reservas Vencidas**: Marca como incumplidas las reservas cuya fecha y hora ya pasaron.
   - [Documentación detallada](scripts/README_VERIFICACION_RESERVAS.md)

Para una visión general de todas las tareas programadas, consulte [README_TAREAS_PROGRAMADAS.md](README_TAREAS_PROGRAMADAS.md).

## Estructura del Proyecto

Para una descripción detallada de la estructura del proyecto, consulte [ESTRUCTURA_PROYECTO.md](ESTRUCTURA_PROYECTO.md).

## Despliegue

El proyecto está configurado para ser desplegado en diferentes entornos:

- **Desarrollo local**: Configuración en `.env.local`
- **Railway**: Plataforma principal de producción
- **PythonAnywhere**: Plataforma alternativa de producción

## API REST

La plataforma expone una API REST para interactuar con el sistema. A continuación se detallan los endpoints disponibles:

### Autenticación

- **Registro de usuario**: `POST /api/auth/registro/`
  - Crea un nuevo usuario y cliente asociado
  - Parámetros: `email`, `password`, `password2`, `nombre`, `apellido`, `tipo_documento`, `numero_documento`, `telefono`, etc.

- **Verificación de email**: `GET /api/auth/verificar-email/{token}/`
  - Verifica el email del usuario mediante un token enviado por correo

- **Inicio de sesión**: `POST /api/auth/login/`
  - Inicia sesión y obtiene token de autenticación
  - Parámetros: `email`, `password`

- **Cierre de sesión**: `POST /api/auth/logout/`
  - Cierra la sesión actual

- **Perfil de usuario**: `GET /api/auth/perfil/`
  - Obtiene información del perfil del usuario autenticado

### Clientes

- **Listar clientes**: `GET /api/clientes/clientes/`
  - Obtiene lista de clientes (solo administradores)

- **Detalle de cliente**: `GET /api/clientes/clientes/{id}/`
  - Obtiene detalles de un cliente específico

- **Historial de servicios**: `GET /api/clientes/clientes/{id}/historial_servicios/`
  - Obtiene el historial de servicios de un cliente

- **Redimir puntos**: `POST /api/clientes/clientes/{id}/redimir_puntos/`
  - Redime puntos acumulados del cliente
  - Parámetros: `puntos`, `descripcion`

### Reservas

- **Listar servicios**: `GET /api/reservas/servicios/`
  - Obtiene lista de servicios disponibles

- **Listar reservas**: `GET /api/reservas/reservas/`
  - Obtiene lista de reservas del usuario o todas (administrador)

- **Crear reserva**: `POST /api/reservas/reservas/`
  - Crea una nueva reserva
  - Parámetros: `servicio`, `fecha_hora`, `notas`

- **Cancelar reserva**: `POST /api/reservas/reservas/{id}/cancelar/`
  - Cancela una reserva existente

- **Confirmar reserva**: `POST /api/reservas/reservas/{id}/confirmar/`
  - Confirma una reserva pendiente (solo administradores)

### Notificaciones

- **Listar notificaciones**: `GET /api/notificaciones/notificaciones/`
  - Obtiene lista de notificaciones del usuario

- **Notificaciones no leídas**: `GET /api/notificaciones/notificaciones/no_leidas/`
  - Obtiene solo las notificaciones no leídas

- **Marcar notificación como leída**: `POST /api/notificaciones/notificaciones/{id}/marcar_leida/`
  - Marca una notificación específica como leída

- **Marcar todas como leídas**: `POST /api/notificaciones/notificaciones/marcar_todas_leidas/`
  - Marca todas las notificaciones como leídas

## Despliegue en Railway

1. Crear una cuenta en [Railway](https://railway.app/)
2. Conectar el repositorio de GitHub
3. Configurar las variables de entorno en Railway
4. Desplegar la aplicación

## Desarrollo

### Estructura del Proyecto

- `autolavados_plataforma/`: Configuración principal del proyecto
- `autenticacion/`: Módulo de autenticación y usuarios
- `clientes/`: Módulo de gestión de clientes
- `reservas/`: Módulo de servicios y reservas
- `notificaciones/`: Módulo de notificaciones

### Comandos Útiles

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar tests
python manage.py test
```

## Sistema de Cancelación Automática de Reservas

El proyecto incluye un sistema automatizado para cancelar reservas pendientes sin pago después de un tiempo configurable (por defecto 5 minutos). Esto permite liberar horarios y recursos cuando los clientes no completan el proceso de pago.

### Componentes del Sistema

- **Comando Django**: `cancelar_reservas_sin_pago` - Identifica y cancela reservas pendientes sin pago
- **Scripts de Ejecución**: Archivos batch y VBS para ejecución silenciosa en Windows
- **Configuración PythonAnywhere**: Script para configurar tareas programadas en el hosting

Para más detalles, consulte la documentación específica en la carpeta `scripts/`:
- `README_TAREAS_PROGRAMADAS.md`: Guía completa de configuración
- `INSTRUCCIONES_TAREA_PROGRAMADA.txt`: Configuración en Windows
- `INSTRUCCIONES_PYTHONANYWHERE.txt`: Configuración en PythonAnywhere

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles.
