# Guía de Despliegue en Railway

Esta guía te ayudará a configurar el despliegue continuo de tu aplicación Django en Railway, permitiéndote mostrar el avance en línea y mantener tu aplicación funcionando siempre.

## Índice

1. [Requisitos previos](#requisitos-previos)
2. [Configuración de Railway](#configuración-de-railway)
3. [Configuración de la base de datos](#configuración-de-la-base-de-datos)
4. [Variables de entorno](#variables-de-entorno)
5. [Despliegue continuo](#despliegue-continuo)
6. [Monitoreo en tiempo real](#monitoreo-en-tiempo-real)
7. [Solución de problemas comunes](#solución-de-problemas-comunes)

## Requisitos previos

Antes de comenzar, asegúrate de tener:

- Una cuenta en [Railway](https://railway.app/)
- Git instalado en tu computadora
- Tu proyecto subido a GitHub
- El archivo `railway.json` configurado (ya está en tu proyecto)

## Configuración de Railway

### Paso 1: Crear una cuenta en Railway

1. Ve a [Railway](https://railway.app/) y regístrate con tu cuenta de GitHub
2. Confirma tu correo electrónico

### Paso 2: Crear un nuevo proyecto

1. En el dashboard de Railway, haz clic en "New Project"
2. Selecciona "Deploy from GitHub repo"
3. Selecciona tu repositorio `autolavados-plataforma`
4. Railway detectará automáticamente que es un proyecto Django gracias al archivo `railway.json`

### Paso 3: Configurar el despliegue

Railway utilizará la configuración en tu archivo `railway.json`, que ya está correctamente configurado:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt && python manage.py collectstatic --noinput"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && gunicorn autolavados_plataforma.wsgi",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## Configuración de la base de datos

### Paso 1: Agregar un servicio de base de datos

1. En tu proyecto de Railway, haz clic en "+ New"
2. Selecciona "Database" y luego "MySQL"
3. Espera a que se aprovisione la base de datos

### Paso 2: Obtener las credenciales de la base de datos

1. Haz clic en el servicio de MySQL que acabas de crear
2. Ve a la pestaña "Connect"
3. Copia la URL de conexión (la necesitarás para las variables de entorno)

## Variables de entorno

### Paso 1: Configurar variables de entorno en Railway

1. Selecciona tu servicio de aplicación web en Railway
2. Ve a la pestaña "Variables"
3. Agrega las siguientes variables:

```
RAILWAY_ENVIRONMENT=production
DATABASE_URL=(la URL de conexión de MySQL)
SECRET_KEY=(una clave secreta larga y aleatoria)
DEBUG=False
ALLOWED_HOSTS=.railway.app,tu-dominio-personalizado.com
SITE_URL=https://tu-app.railway.app

# Configuración de correo (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-correo@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-de-aplicacion
```

### Paso 2: Habilitar la configuración de correo en producción

Edita el archivo `settings.py` para usar la configuración de correo en producción:

1. Busca la sección de configuración de correo electrónico
2. Descomenta las líneas de configuración SMTP para producción

## Despliegue continuo

### Paso 1: Configurar despliegue automático

Railway ya está configurado para desplegar automáticamente cuando haces push a la rama principal de tu repositorio GitHub.

### Paso 2: Verificar el despliegue

1. Haz un pequeño cambio en tu código
2. Haz commit y push a GitHub
3. Ve a Railway y observa cómo se inicia automáticamente un nuevo despliegue
4. Verifica que tu aplicación se actualice correctamente

## Monitoreo en tiempo real

### Paso 1: Configurar monitoreo básico

1. En tu proyecto de Railway, ve a la pestaña "Metrics"
2. Aquí puedes ver el uso de CPU, memoria y otros recursos

### Paso 2: Configurar alertas (opcional)

1. Ve a la pestaña "Settings" de tu proyecto
2. Configura notificaciones por correo electrónico para eventos importantes

## Solución de problemas comunes

### Error en la migración de la base de datos

Si tienes problemas con las migraciones:

1. Ve a la pestaña "Shell" de tu servicio web en Railway
2. Ejecuta: `python manage.py migrate --fake-initial`

### Problemas con archivos estáticos

Si los archivos estáticos no se cargan correctamente:

1. Verifica que `STATIC_ROOT` esté configurado correctamente en `settings.py`
2. Asegúrate de que `whitenoise` esté instalado y configurado
3. Ejecuta manualmente `python manage.py collectstatic --noinput` en la shell de Railway

### Errores de conexión a la base de datos

Si hay problemas de conexión a la base de datos:

1. Verifica que la variable `DATABASE_URL` esté correctamente configurada
2. Asegúrate de que el servicio de MySQL esté funcionando
3. Prueba la conexión manualmente desde la shell de Railway

---

Siguiendo esta guía, tendrás tu aplicación desplegada en Railway con actualizaciones automáticas cada vez que hagas cambios en tu código. Railway se encargará de mantener tu aplicación en línea y disponible para tus usuarios.