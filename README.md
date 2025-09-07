# Proyecto_CarWash_Maicao
Plataforma Integral para Autolavados con Monitoreo y Fidelización en Maicao, La Guajira

## Configuración del Proyecto

### Requisitos

- Python 3.10+
- MySQL 8.0+ o SQLite (desarrollo)
- Pip
- Visual Studio Code (opcional)

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

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles.
