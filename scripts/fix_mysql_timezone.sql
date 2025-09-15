-- Script para corregir problemas de zona horaria en MySQL
-- Este script configura la zona horaria del servidor MySQL y actualiza la configuración

-- Establecer la zona horaria del servidor a America/Bogota (COT)
SET GLOBAL time_zone = '-05:00';
SET time_zone = '-05:00';

-- Verificar la configuración actual de zona horaria
SELECT @@global.time_zone, @@session.time_zone;

-- Mostrar las zonas horarias disponibles (si las tablas de zona horaria están cargadas)
SELECT * FROM mysql.time_zone_name LIMIT 10;

-- Si las tablas de zona horaria no están cargadas, verás un error en el comando anterior
-- En ese caso, necesitas cargar las tablas de zona horaria usando mysql_tzinfo_to_sql

-- Si las tablas de zona horaria están cargadas, también se puede usar el nombre de la zona
-- SET GLOBAL time_zone = 'America/Bogota';
-- SET time_zone = 'America/Bogota';

-- Nota: Actualmente estamos usando el offset directo (-05:00) que corresponde a Bogotá (COT)

-- Aplicar los cambios
FLUSH PRIVILEGES;