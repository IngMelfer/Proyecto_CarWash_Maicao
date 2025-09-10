#!/bin/bash

# Script para migrar de SQLite a MySQL
echo "Iniciando migración de SQLite a MySQL..."

# 1. Crear la base de datos MySQL si no existe
echo "Creando base de datos MySQL..."
echo "CREATE DATABASE IF NOT EXISTS autolavados_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" | mysql -u root

# 2. Crear usuario y asignar permisos
echo "Creando usuario y asignando permisos..."
echo "CREATE USER IF NOT EXISTS 'autolavados_user'@'localhost' IDENTIFIED BY 'autolavados_password';" | mysql -u root
echo "GRANT ALL PRIVILEGES ON autolavados_db.* TO 'autolavados_user'@'localhost';" | mysql -u root
echo "FLUSH PRIVILEGES;" | mysql -u root

# 3. Hacer un respaldo de la base de datos SQLite
echo "Haciendo respaldo de la base de datos SQLite..."
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data_backup.json

# 4. Aplicar migraciones a la base de datos MySQL
echo "Aplicando migraciones a MySQL..."
python manage.py migrate

# 5. Cargar los datos respaldados en MySQL
echo "Cargando datos en MySQL..."
python manage.py loaddata data_backup.json

echo "Migración completada con éxito!"
echo "Recuerda verificar que todo funcione correctamente."