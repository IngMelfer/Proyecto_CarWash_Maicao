-- Script para corregir problemas de zona horaria en MySQL
-- Este script configura la zona horaria del servidor MySQL y actualiza la configuración

-- Establecer la zona horaria del servidor a UTC
SET GLOBAL time_zone = '+00:00';
SET time_zone = '+00:00';

-- Verificar la configuración actual de zona horaria
SELECT @@global.time_zone, @@session.time_zone;

-- Mostrar las zonas horarias disponibles (si las tablas de zona horaria están cargadas)
SELECT * FROM mysql.time_zone_name LIMIT 10;

-- Si las tablas de zona horaria no están cargadas, verás un error en el comando anterior
-- En ese caso, necesitas cargar las tablas de zona horaria usando mysql_tzinfo_to_sql

-- Para establecer la zona horaria a America/Bogota (si las tablas están cargadas)
-- SET GLOBAL time_zone = 'America/Bogota';
-- SET time_zone = 'America/Bogota';

-- Aplicar los cambios
FLUSH PRIVILEGES;