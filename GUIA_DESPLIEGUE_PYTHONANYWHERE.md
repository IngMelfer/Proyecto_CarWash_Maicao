# Guía de Despliegue en PythonAnywhere

## Descripción General

Esta guía proporciona instrucciones paso a paso para desplegar la Plataforma de Autolavados en [PythonAnywhere](https://www.pythonanywhere.com/), un servicio de hosting especializado en aplicaciones Python que ofrece una alternativa económica y fácil de configurar.

## Requisitos Previos

1. Cuenta en [PythonAnywhere](https://www.pythonanywhere.com/) (gratuita o de pago)
2. Repositorio Git con el código del proyecto
3. Variables de entorno configuradas para producción

## Pasos para el Despliegue

### 1. Preparación del Proyecto

#### Asegúrese de que su proyecto incluya los siguientes archivos:

- `requirements.txt`: Lista de dependencias de Python
- Configuración de Django para producción

### 2. Configuración en PythonAnywhere

1. **Inicie sesión en PythonAnywhere**
   - Vaya a [PythonAnywhere](https://www.pythonanywhere.com/) e inicie sesión con su cuenta

2. **Abra una consola Bash**
   - Haga clic en "Consoles" en el menú superior
   - Seleccione "Bash" para abrir una nueva consola

3. **Clone el repositorio**
   ```bash
   git clone https://github.com/su-usuario/autolavados-plataforma.git
   cd autolavados-plataforma
   ```

4. **Cree un entorno virtual**
   ```bash
   mkvirtualenv --python=python3.10 autolavados-venv
   ```

5. **Instale las dependencias**
   ```bash
   pip install -r requirements.txt
   pip install mysqlclient  # PythonAnywhere usa MySQL por defecto
   ```

6. **Configure las variables de entorno**
   - Cree un archivo `.env` en el directorio del proyecto
   ```bash
   nano .env
   ```
   - Agregue las siguientes variables:
   ```
   DEBUG=False
   SECRET_KEY=su_clave_secreta_segura
   ALLOWED_HOSTS=.pythonanywhere.com,su-dominio-personalizado.com
   DJANGO_SETTINGS_MODULE=autolavados_plataforma.settings.production
   ```

7. **Configure la base de datos**
   - Vaya a la pestaña "Databases"
   - Inicialice una base de datos MySQL si aún no lo ha hecho
   - Anote el nombre de usuario, contraseña y nombre de la base de datos
   - Agregue la configuración de la base de datos a su archivo `.env`:
   ```
   DATABASE_URL=mysql://usuario:contraseña@usuario.mysql.pythonanywhere-services.com/usuario$nombre_db
   ```

8. **Ejecute las migraciones**
   ```bash
   python manage.py migrate
   ```

9. **Recopile los archivos estáticos**
   ```bash
   python manage.py collectstatic --noinput
   ```

### 3. Configuración de la Aplicación Web

1. **Vaya a la pestaña "Web"**
   - Haga clic en "Add a new web app"

2. **Configure la aplicación web**
   - Seleccione "Manual configuration"
   - Seleccione la versión de Python que coincida con su entorno virtual (Python 3.10)

3. **Configure la ruta del código**
   - En "Code" sección, establezca la ruta al directorio del proyecto:
   ```
   /home/su-usuario/autolavados-plataforma
   ```

4. **Configure el entorno virtual**
   - En "Virtualenv" sección, establezca la ruta al entorno virtual:
   ```
   /home/su-usuario/.virtualenvs/autolavados-venv
   ```

5. **Configure el archivo WSGI**
   - Haga clic en el enlace al archivo WSGI
   - Reemplace el contenido con lo siguiente:
   ```python
   import os
   import sys
   import dotenv
   from pathlib import Path
   
   # Ruta al directorio del proyecto
   path = '/home/su-usuario/autolavados-plataforma'
   if path not in sys.path:
       sys.path.append(path)
   
   # Cargar variables de entorno desde .env
   dotenv_file = Path(path) / '.env'
   if dotenv_file.exists():
       dotenv.load_dotenv(dotenv_file)
   
   # Configurar Django
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autolavados_plataforma.settings.production')
   
   # Importar la aplicación WSGI
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

6. **Configure los archivos estáticos**
   - En "Static files" sección, agregue:
     - URL: `/static/`
     - Directory: `/home/su-usuario/autolavados-plataforma/static`
   - Si tiene archivos de medios, agregue:
     - URL: `/media/`
     - Directory: `/home/su-usuario/autolavados-plataforma/media`

7. **Reinicie la aplicación web**
   - Haga clic en el botón "Reload" para aplicar los cambios

### 4. Configuración de Dominio Personalizado (Opcional)

1. **Agregue un dominio personalizado**
   - Vaya a la pestaña "Web"
   - En "Add a new domain", ingrese su dominio personalizado

2. **Configure los registros DNS**
   - Siga las instrucciones proporcionadas por PythonAnywhere para configurar los registros CNAME en su proveedor de dominio

### 5. Configuración de Tareas Programadas

PythonAnywhere ofrece un sistema integrado de tareas programadas:

1. **Vaya a la pestaña "Tasks"**

2. **Configure las tareas programadas**
   - Para cancelación de reservas sin pago (cada 5 minutos):
     ```bash
     cd /home/su-usuario/autolavados-plataforma && python manage.py cancelar_reservas_sin_pago
     ```
   - Para verificación de reservas vencidas (cada hora):
     ```bash
     cd /home/su-usuario/autolavados-plataforma && python manage.py verificar_reservas_vencidas
     ```

3. **Configuración automática con script**
   - Alternativamente, puede usar el script proporcionado:
     ```bash
     cd /home/su-usuario/autolavados-plataforma/scripts && python configurar_tarea_pythonanywhere.py --username su-usuario --token su-token-api
     ```

### 6. Actualizaciones y Mantenimiento

1. **Actualización del código**
   - Abra una consola Bash
   - Navegue al directorio del proyecto
   - Actualice el código desde Git:
     ```bash
     cd /home/su-usuario/autolavados-plataforma
     git pull
     ```
   - Aplique las migraciones si es necesario:
     ```bash
     python manage.py migrate
     ```
   - Recopile los archivos estáticos si es necesario:
     ```bash
     python manage.py collectstatic --noinput
     ```
   - Reinicie la aplicación web desde la pestaña "Web"

2. **Monitoreo**
   - Utilice la pestaña "Web" para ver los logs de error y acceso
   - Configure notificaciones por correo electrónico para errores

## Solución de Problemas

### Error 502 Bad Gateway

Si recibe un error 502 después del despliegue:

1. Verifique los logs de error:
   - Vaya a la pestaña "Web"
   - Haga clic en "Error log"

2. Problemas comunes:
   - Dependencias faltantes: Asegúrese de que todas las dependencias estén instaladas
   - Configuración WSGI incorrecta: Verifique el archivo WSGI
   - Permisos de archivos: Asegúrese de que los archivos tengan los permisos correctos

### Problemas con Archivos Estáticos

Si los archivos estáticos no se cargan correctamente:

1. Verifique la configuración de archivos estáticos en la pestaña "Web"
2. Asegúrese de haber ejecutado `collectstatic`
3. Verifique que `STATIC_URL` y `STATIC_ROOT` estén configurados correctamente en su configuración de producción

### Problemas con Tareas Programadas

Si las tareas programadas no se ejecutan correctamente:

1. Verifique los logs de las tareas:
   - Vaya a la pestaña "Tasks"
   - Haga clic en "View task log" junto a la tarea

2. Problemas comunes:
   - Ruta incorrecta: Asegúrese de que la ruta al proyecto sea correcta
   - Entorno virtual no activado: Asegúrese de activar el entorno virtual en el comando
   - Permisos insuficientes: Asegúrese de que el usuario tenga permisos para ejecutar el comando

## Limitaciones de la Cuenta Gratuita

Si está utilizando una cuenta gratuita de PythonAnywhere, tenga en cuenta las siguientes limitaciones:

1. **CPU y RAM limitadas**: Las aplicaciones pueden ser más lentas
2. **Tiempo de ejecución limitado**: Las tareas programadas tienen un límite de tiempo de ejecución
3. **Dominio personalizado no disponible**: Solo puede usar el subdominio `.pythonanywhere.com`
4. **Acceso a Internet limitado**: Solo puede acceder a ciertos sitios web externos
5. **Tareas programadas limitadas**: Solo puede programar tareas diarias, no por hora o minuto

Considere actualizar a una cuenta de pago si necesita superar estas limitaciones.

## Recursos Adicionales

- [Documentación oficial de PythonAnywhere](https://help.pythonanywhere.com/)
- [Guía de Django en PythonAnywhere](https://help.pythonanywhere.com/pages/Django/)
- [Optimización de aplicaciones Django para producción](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)

## Contacto

Si tiene problemas con el despliegue en PythonAnywhere, contacte al administrador del sistema o consulte la documentación oficial de PythonAnywhere.