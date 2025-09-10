# Migración de SQLite a MySQL

Este documento describe el proceso para migrar la base de datos de SQLite a MySQL local de manera limpia.

## Requisitos previos

1. MySQL instalado y configurado en tu sistema
2. Permisos de administrador en MySQL para crear bases de datos y usuarios

## Pasos para la migración

### 1. Configuración del entorno

La configuración ya ha sido actualizada en los siguientes archivos:

- `settings.py`: Se ha cambiado `USE_MYSQL = True` para usar MySQL
- `requirements.txt` y `requirements-local.txt`: Se han habilitado las dependencias de MySQL
- `.env.local`: Contiene las variables de entorno para la conexión a MySQL

### 2. Instalar dependencias

```
pip install -r requirements-local.txt
```

Esto instalará `mysqlclient` y `PyMySQL` necesarios para la conexión a MySQL.

### 3. Crear la base de datos MySQL

Puedes usar el script proporcionado `migrar_a_mysql.ps1` para Windows o crear la base de datos manualmente:

```sql
CREATE DATABASE autolavados_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'autolavados_user'@'localhost' IDENTIFIED BY 'autolavados_password';
GRANT ALL PRIVILEGES ON autolavados_db.* TO 'autolavados_user'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Migración de datos

Para migrar los datos de SQLite a MySQL, sigue estos pasos:

1. Hacer un respaldo de la base de datos SQLite:
   ```
   python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data_backup.json
   ```

2. Aplicar migraciones a la base de datos MySQL:
   ```
   python manage.py migrate
   ```

3. Cargar los datos respaldados en MySQL:
   ```
   python manage.py loaddata data_backup.json
   ```

### 5. Verificación

Para verificar que la migración se realizó correctamente:

1. Inicia el servidor de desarrollo:
   ```
   python manage.py runserver
   ```

2. Accede a la aplicación y verifica que los datos se muestren correctamente
3. Verifica que puedas crear, editar y eliminar registros

### 6. Automatización

Para automatizar todo el proceso, puedes ejecutar el script PowerShell incluido:

```
.\migrar_a_mysql.ps1
```

Este script realizará todos los pasos necesarios para la migración.

## Solución de problemas

### Error de conexión a MySQL

Si encuentras errores de conexión, verifica:

1. Que MySQL esté en ejecución
2. Que las credenciales en `.env.local` sean correctas
3. Que el usuario tenga los permisos adecuados

### Errores en la carga de datos

Si hay errores al cargar los datos:

1. Verifica que el formato del archivo JSON sea correcto
2. Asegúrate de que las migraciones se hayan aplicado correctamente
3. Considera migrar app por app si hay problemas con dependencias

## Volver a SQLite

Si necesitas volver a SQLite, simplemente cambia `USE_MYSQL = False` en `settings.py`.