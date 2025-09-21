# Guía de Despliegue en PythonAnywhere

## Sistema de Autolavado - Maicao

Esta guía te ayudará a desplegar el sistema de autolavado en PythonAnywhere después de subirlo a GitHub.

---

## 📋 Requisitos Previos

- [ ] Cuenta en PythonAnywhere (plan Hacker o superior para MySQL)
- [ ] Repositorio en GitHub con el código actualizado
- [ ] Acceso a la configuración de base de datos MySQL en PythonAnywhere

---

## 🚀 Paso 1: Preparación del Repositorio en GitHub

### 1.1 Verificar archivos importantes
Asegúrate de que estos archivos estén en tu repositorio:
- `requirements.txt` (actualizado)
- `.env.example` (configuración de ejemplo)
- `manage.py`
- Todas las migraciones en `*/migrations/`

### 1.2 Archivos a NO subir (verificar .gitignore)
```
.env
*.pyc
__pycache__/
db.sqlite3
staticfiles/
media/
sent_emails/
```

---

## 🔧 Paso 2: Configuración en PythonAnywhere

### 2.1 Clonar el repositorio
```bash
# En la consola Bash de PythonAnywhere
cd ~
git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
```

### 2.2 Crear entorno virtual
```bash
# Crear entorno virtual con Python 3.10
mkvirtualenv --python=/usr/bin/python3.10 autolavados_env

# Activar entorno virtual
workon autolavados_env

# Instalar dependencias
pip install -r requirements.txt
```

### 2.3 Configurar variables de entorno
```bash
# Crear archivo .env
cp .env.example .env
nano .env
```

Configurar las siguientes variables en `.env`:
```env
# CONFIGURACIÓN DE SEGURIDAD
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura_generada
DEBUG=False
ALLOWED_HOSTS=tu_usuario.pythonanywhere.com

# BASE DE DATOS MYSQL
USE_MYSQL=True
DB_NAME=tu_usuario$autolavados_db
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña_mysql_pythonanywhere
DB_HOST=tu_usuario.mysql.pythonanywhere-services.com
DB_PORT=3306

# ARCHIVOS ESTÁTICOS
STATIC_URL=/static/
STATIC_ROOT=/home/tu_usuario/tu_repositorio/staticfiles
STATIC_DIR=/home/tu_usuario/tu_repositorio/static

# ARCHIVOS MEDIA
MEDIA_URL=/media/
MEDIA_ROOT=/home/tu_usuario/tu_repositorio/media

# CSRF Y SESIONES
CSRF_TRUSTED_ORIGINS=https://tu_usuario.pythonanywhere.com
SESSION_COOKIE_SECURE=True

# CORREO ELECTRÓNICO (opcional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion
EMAIL_USE_TLS=True

# URL DEL SITIO
SITE_URL=https://tu_usuario.pythonanywhere.com

# LOGGING
LOG_LEVEL=INFO
DJANGO_LOG_LEVEL=INFO
APP_LOG_LEVEL=INFO
```

---

## 🗄️ Paso 3: Configuración de Base de Datos

### 3.1 Crear base de datos MySQL
1. Ve a la pestaña "Databases" en tu dashboard de PythonAnywhere
2. Crea una nueva base de datos llamada `autolavados_db`
3. Anota las credenciales de conexión

### 3.2 Ejecutar migraciones
```bash
# Activar entorno virtual
workon autolavados_env
cd ~/tu_repositorio

# Verificar configuración de base de datos
python manage.py check

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

---

## 🌐 Paso 4: Configuración de la Aplicación Web

### 4.1 Crear aplicación web
1. Ve a la pestaña "Web" en tu dashboard
2. Clic en "Add a new web app"
3. Selecciona "Manual configuration"
4. Selecciona Python 3.10

### 4.2 Configurar WSGI
Edita el archivo WSGI (`/var/www/tu_usuario_pythonanywhere_com_wsgi.py`):

```python
import os
import sys

# Agregar el directorio del proyecto al path
path = '/home/tu_usuario/tu_repositorio'
if path not in sys.path:
    sys.path.insert(0, path)

# Configurar Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'autolavados_plataforma.settings'

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

# Configurar aplicación WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 4.3 Configurar entorno virtual
En la pestaña "Web", sección "Virtualenv":
```
/home/tu_usuario/.virtualenvs/autolavados_env
```

### 4.4 Configurar archivos estáticos
En la pestaña "Web", sección "Static files":
- URL: `/static/`
- Directory: `/home/tu_usuario/tu_repositorio/staticfiles/`

- URL: `/media/`
- Directory: `/home/tu_usuario/tu_repositorio/media/`

---

## 🔒 Paso 5: Configuración de Seguridad

### 5.1 Generar SECRET_KEY segura
```python
# En la consola Python de PythonAnywhere
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 5.2 Configurar HTTPS
- PythonAnywhere proporciona HTTPS automáticamente
- Asegúrate de que `SESSION_COOKIE_SECURE=True` en producción

---

## 📊 Paso 6: Datos Iniciales (Opcional)

### 6.1 Crear datos de prueba
```bash
# Ejecutar script de creación de bahías
python manage.py shell < scripts/crear_bahias.py

# O crear manualmente desde el admin
python manage.py runserver
# Ir a /admin/ y crear servicios, bahías, etc.
```

---

## 🧪 Paso 7: Pruebas de Funcionamiento

### 7.1 Verificar la aplicación
1. Ve a `https://tu_usuario.pythonanywhere.com`
2. Verifica que la página principal carga correctamente
3. Prueba el login en `/autenticacion/login/`
4. Verifica el panel de administración en `/admin/`

### 7.2 Pruebas de funcionalidad
- [ ] Registro de usuarios
- [ ] Login/logout
- [ ] Creación de reservas
- [ ] Panel de administración
- [ ] API endpoints
- [ ] Archivos estáticos (CSS, JS, imágenes)

---

## 🔄 Paso 8: Actualizaciones Futuras

### 8.1 Script de actualización
Crea un script `update.sh`:
```bash
#!/bin/bash
cd ~/tu_repositorio
git pull origin main
workon autolavados_env
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
# Reiniciar aplicación web desde el dashboard
```

### 8.2 Proceso de actualización
1. Hacer cambios en el código local
2. Commit y push a GitHub
3. En PythonAnywhere: ejecutar script de actualización
4. Reiniciar la aplicación web desde el dashboard

---

## 🚨 Solución de Problemas Comunes

### Error de base de datos
```bash
# Verificar conexión
python manage.py dbshell

# Verificar configuración
python manage.py check --database default
```

### Error de archivos estáticos
```bash
# Recolectar archivos estáticos
python manage.py collectstatic --clear --noinput

# Verificar permisos
ls -la staticfiles/
```

### Error de importación
```bash
# Verificar path de Python
python -c "import sys; print(sys.path)"

# Verificar instalación de dependencias
pip list
```

### Error 500
1. Revisar logs de error en la pestaña "Web"
2. Verificar configuración de `DEBUG=False`
3. Verificar `ALLOWED_HOSTS`
4. Revisar archivo WSGI

---

## 📝 Lista de Verificación Final

- [ ] Repositorio subido a GitHub
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas
- [ ] Variables de entorno configuradas
- [ ] Base de datos creada y migrada
- [ ] Superusuario creado
- [ ] Archivos estáticos recolectados
- [ ] Aplicación web configurada
- [ ] WSGI configurado correctamente
- [ ] Archivos estáticos mapeados
- [ ] Aplicación funcionando en producción
- [ ] Pruebas de funcionalidad completadas

---

## 📞 Soporte

Si encuentras problemas durante el despliegue:

1. Revisa los logs de error en PythonAnywhere
2. Verifica la configuración paso a paso
3. Consulta la documentación de PythonAnywhere
4. Revisa los issues del repositorio en GitHub

---

**¡Felicidades! Tu sistema de autolavado está ahora desplegado en PythonAnywhere.**