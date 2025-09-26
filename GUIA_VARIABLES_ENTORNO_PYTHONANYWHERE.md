# Guía de Variables de Entorno para PythonAnywhere

## Variables Requeridas para el Funcionamiento Correcto

### 1. Variables de Base de Datos MySQL
```bash
# En el dashboard de PythonAnywhere, ir a Files > .bashrc o crear un archivo .env
export USE_MYSQL=True
export DB_NAME="tu_usuario$autolavados"  # Reemplazar 'tu_usuario' con tu username de PythonAnywhere
export DB_USER="tu_usuario"              # Tu username de PythonAnywhere
export DB_PASSWORD="tu_password_mysql"   # Password de tu base de datos MySQL
export DB_HOST="tu_usuario.mysql.pythonanywhere-services.com"
export DB_PORT="3306"
```

### 2. Variables de Configuración del Sitio
```bash
export PYTHONANYWHERE_USERNAME="tu_usuario"  # Tu username de PythonAnywhere
export SITE_URL="https://tu_usuario.pythonanywhere.com"
export CUSTOM_DOMAIN=""  # Si tienes un dominio personalizado
```

### 3. Variables de Django
```bash
export DJANGO_SETTINGS_MODULE="autolavados_plataforma.settings_production"
export SECRET_KEY="tu_clave_secreta_muy_larga_y_segura"
export DEBUG=False
```

### 4. Variables de Correo Electrónico (Opcional)
```bash
export EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
export EMAIL_HOST="smtp.gmail.com"
export EMAIL_PORT="587"
export EMAIL_HOST_USER="tu_email@gmail.com"
export EMAIL_HOST_PASSWORD="tu_password_de_aplicacion"
export EMAIL_USE_TLS="True"
export DEFAULT_FROM_EMAIL="noreply@premiumcardetailing.com"
```

### 5. Variables de Nequi (Si usas pagos)
```bash
export NEQUI_API_KEY="tu_api_key"
export NEQUI_CLIENT_ID="tu_client_id"
export NEQUI_CLIENT_SECRET="tu_client_secret"
export NEQUI_BASE_URL="https://api.nequi.com.co"
export NEQUI_SANDBOX="False"  # True para pruebas, False para producción
```

## Cómo Configurar las Variables en PythonAnywhere

### Método 1: Archivo .bashrc
1. Ve a **Files** en tu dashboard de PythonAnywhere
2. Abre el archivo `.bashrc` en tu directorio home
3. Agrega las variables al final del archivo:
```bash
# Variables de entorno para autolavados
export USE_MYSQL=True
export DB_NAME="tu_usuario$autolavados"
# ... resto de variables
```
4. Guarda el archivo
5. Reinicia tu aplicación web

### Método 2: Archivo .env (Recomendado)
1. Crea un archivo `.env` en el directorio de tu proyecto
2. Agrega las variables sin `export`:
```
USE_MYSQL=True
DB_NAME=tu_usuario$autolavados
DB_USER=tu_usuario
# ... resto de variables
```
3. Asegúrate de que tu aplicación cargue este archivo

### Método 3: Variables en WSGI
Puedes agregar las variables directamente en tu archivo `wsgi.py`:
```python
import os
os.environ.setdefault('USE_MYSQL', 'True')
os.environ.setdefault('DB_NAME', 'tu_usuario$autolavados')
# ... resto de variables
```

## Verificación de Variables
Para verificar que las variables están configuradas correctamente:

1. Abre una consola Bash en PythonAnywhere
2. Ejecuta: `echo $USE_MYSQL` (debería mostrar "True")
3. Ejecuta: `echo $DB_NAME` (debería mostrar tu nombre de base de datos)

## Problemas Comunes

### Error: "Por favor complete todos los campos requeridos"
- **Causa**: Falta `CSRF_TRUSTED_ORIGINS` o variables de base de datos
- **Solución**: Verificar que todas las variables estén configuradas

### Error de Conexión a Base de Datos
- **Causa**: Variables de MySQL incorrectas
- **Solución**: Verificar `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`

### Error 500 Internal Server Error
- **Causa**: `SECRET_KEY` no configurada o `DEBUG=True` en producción
- **Solución**: Configurar `SECRET_KEY` y `DEBUG=False`

## Comandos Útiles para Diagnóstico

```bash
# Verificar variables de entorno
env | grep -E "(DB_|USE_MYSQL|DJANGO_|SITE_URL)"

# Probar conexión a base de datos
python manage.py dbshell

# Verificar configuración de Django
python manage.py check --deploy

# Ver logs de errores
tail -f /var/log/tu_usuario.pythonanywhere.com.error.log
```

## Notas Importantes

1. **Nunca** subas el archivo `.env` a GitHub (debe estar en `.gitignore`)
2. Usa contraseñas seguras para la base de datos
3. Reinicia la aplicación web después de cambiar variables de entorno
4. Las variables de entorno tienen prioridad sobre los valores por defecto en `settings.py`