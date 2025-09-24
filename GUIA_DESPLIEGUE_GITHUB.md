# Guía de Despliegue - CarWash Maicao

## 📋 Preparación para Despliegue en GitHub

Esta guía detalla los pasos necesarios para preparar y desplegar el sistema CarWash Maicao en GitHub y posteriormente en plataformas de hosting.

## 🔧 Configuración Previa

### 1. Variables de Entorno

El proyecto utiliza variables de entorno para configuración. Copia el archivo `.env.example` a `.env` y configura las siguientes variables:

```bash
# Configuración de Base de Datos
USE_MYSQL=True
DB_NAME=autolavados_db
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=3306

# Configuración de Seguridad
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# Configuración de Archivos Estáticos
STATIC_URL=/static/
STATIC_ROOT=staticfiles
MEDIA_URL=/media/
MEDIA_ROOT=media
```

### 2. Dependencias

El archivo `requirements.txt` contiene todas las dependencias necesarias:

```
asgiref==3.8.1
cffi==1.17.1
Django==5.1.4
djangorestframework==3.15.2
gunicorn==23.0.0
mysqlclient==2.2.6
PyMySQL==1.1.1
python-dotenv==1.0.1
sentry-sdk==2.19.2
whitenoise==6.8.2
# ... y más dependencias
```

## 🚀 Pasos de Despliegue

### 1. Preparación del Repositorio

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/carwash-maicao.git
cd carwash-maicao

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración de Base de Datos

```bash
# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic --noinput
```

### 3. Configuración para Producción

#### Settings de Producción

El archivo `settings.py` está configurado para usar variables de entorno:

- `DEBUG=False` en producción
- `ALLOWED_HOSTS` configurado según el dominio
- `SECRET_KEY` desde variable de entorno
- Base de datos MySQL configurada
- Archivos estáticos con WhiteNoise

#### Middleware de Seguridad

- `SecurityMiddleware` para headers de seguridad
- `WhiteNoiseMiddleware` para archivos estáticos
- `CsrfViewMiddleware` para protección CSRF
- Middleware personalizado para manejo de errores

## 🌐 Opciones de Hosting

### 1. PythonAnywhere

```bash
# Variables de entorno para PythonAnywhere
USE_MYSQL=True
DB_NAME=tu_usuario$autolavados_db
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña_pythonanywhere
DB_HOST=tu_usuario.mysql.pythonanywhere-services.com
DB_PORT=3306
DEBUG=False
ALLOWED_HOSTS=tu_usuario.pythonanywhere.com
```

### 2. Railway

```bash
# Variables de entorno para Railway
USE_MYSQL=False  # Railway usa PostgreSQL
DATABASE_URL=postgresql://...
DEBUG=False
ALLOWED_HOSTS=tu-app.railway.app
```

### 3. Heroku

```bash
# Procfile incluido
web: gunicorn autolavados_plataforma.wsgi:application

# Variables de entorno
DEBUG=False
ALLOWED_HOSTS=tu-app.herokuapp.com
```

## 📁 Estructura del Proyecto

```
carwash-maicao/
├── autenticacion/          # Módulo de autenticación
├── clientes/              # Gestión de clientes
├── empleados/             # Gestión de empleados
├── reservas/              # Sistema de reservas
├── notificaciones/        # Sistema de notificaciones
├── static/                # Archivos estáticos
├── templates/             # Plantillas HTML
├── media/                 # Archivos subidos
├── requirements.txt       # Dependencias
├── .env.example          # Ejemplo de variables de entorno
├── .gitignore            # Archivos ignorados por Git
├── manage.py             # Script de gestión Django
└── README.md             # Documentación principal
```

## 🔒 Seguridad

### Configuraciones de Seguridad Implementadas

1. **CSRF Protection**: Habilitado con tokens
2. **Session Security**: Cookies seguras configuradas
3. **CORS**: Configurado para orígenes específicos
4. **SQL Injection**: Protección mediante ORM de Django
5. **XSS Protection**: Headers de seguridad configurados

### Variables Sensibles

Nunca incluir en el repositorio:
- `.env` (archivo de variables de entorno)
- `db.sqlite3` (base de datos local)
- Archivos de log
- Claves privadas

## 🧪 Testing

El sistema incluye pruebas completas:

```bash
# Ejecutar pruebas del sistema
python test_database.py
python test_api_rest.py
python test_ui_responsividad.py
```

## 📊 Monitoreo

### Logging Configurado

- Logs de Django request
- Logs de middleware personalizado
- Configuración de niveles por entorno

### Sentry (Opcional)

```python
# Configuración de Sentry para monitoreo de errores
SENTRY_DSN=tu_dsn_de_sentry
```

## 🔄 Actualizaciones

### Proceso de Actualización

1. Hacer backup de la base de datos
2. Actualizar código desde Git
3. Instalar nuevas dependencias
4. Ejecutar migraciones
5. Recopilar archivos estáticos
6. Reiniciar servidor

```bash
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

## 📞 Soporte

Para soporte técnico o reportar problemas:

1. Revisar los logs del sistema
2. Verificar configuración de variables de entorno
3. Consultar la documentación específica del módulo
4. Crear issue en GitHub si es necesario

## 📝 Notas Importantes

- El sistema está optimizado para MySQL en producción
- SQLite solo para desarrollo local
- Archivos estáticos servidos por WhiteNoise
- Sistema de autenticación personalizado implementado
- API REST disponible para integraciones

---

**Fecha de última actualización**: Enero 2025
**Versión del sistema**: 1.0.0
**Estado**: Listo para producción ✅