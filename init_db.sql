-- Script para inicializar la base de datos MySQL para el proyecto de autolavados

-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS autolavados_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear el usuario para la aplicación si no existe
CREATE USER IF NOT EXISTS 'autolavados_user'@'localhost' IDENTIFIED BY 'autolavados_password';

-- Otorgar privilegios al usuario sobre la base de datos
GRANT ALL PRIVILEGES ON autolavados_db.* TO 'autolavados_user'@'localhost';

-- Aplicar los cambios
FLUSH PRIVILEGES;

-- Mensaje de confirmación
SELECT 'Base de datos y usuario creados correctamente' AS mensaje;