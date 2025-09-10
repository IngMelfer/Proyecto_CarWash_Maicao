# Script PowerShell para migrar de SQLite a MySQL en Windows

Write-Host "Iniciando migración de SQLite a MySQL..." -ForegroundColor Green

# 1. Verificar que MySQL esté instalado y accesible
Write-Host "Verificando instalación de MySQL..." -ForegroundColor Yellow
try {
    mysql --version
    Write-Host "MySQL encontrado!" -ForegroundColor Green
} catch {
    Write-Host "Error: MySQL no está instalado o no está en el PATH. Por favor, instala MySQL y asegúrate de que esté en el PATH." -ForegroundColor Red
    exit 1
}

# 2. Crear la base de datos MySQL si no existe
Write-Host "Creando base de datos MySQL..." -ForegroundColor Yellow
mysql -u root -e "CREATE DATABASE IF NOT EXISTS autolavados_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 3. Crear usuario y asignar permisos
Write-Host "Creando usuario y asignando permisos..." -ForegroundColor Yellow
mysql -u root -e "CREATE USER IF NOT EXISTS 'autolavados_user'@'localhost' IDENTIFIED BY 'autolavados_password';"
mysql -u root -e "GRANT ALL PRIVILEGES ON autolavados_db.* TO 'autolavados_user'@'localhost';"
mysql -u root -e "FLUSH PRIVILEGES;"

# 4. Hacer un respaldo de la base de datos SQLite
Write-Host "Haciendo respaldo de la base de datos SQLite..." -ForegroundColor Yellow
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data_backup.json

# 5. Aplicar migraciones a la base de datos MySQL
Write-Host "Aplicando migraciones a MySQL..." -ForegroundColor Yellow
python manage.py migrate

# 6. Cargar los datos respaldados en MySQL
Write-Host "Cargando datos en MySQL..." -ForegroundColor Yellow
python manage.py loaddata data_backup.json

Write-Host "Migración completada con éxito!" -ForegroundColor Green
Write-Host "Recuerda verificar que todo funcione correctamente." -ForegroundColor Cyan