-- Script para crear y poblar las tablas de zona horaria en MySQL
-- Este script debe ejecutarse como usuario root o con privilegios en la base de datos mysql

USE mysql;

-- Crear tablas de zona horaria si no existen
CREATE TABLE IF NOT EXISTS time_zone (
  Time_zone_id int unsigned NOT NULL auto_increment,
  Use_leap_seconds enum('Y','N') NOT NULL default 'N',
  PRIMARY KEY (Time_zone_id)
) CHARACTER SET utf8 COMMENT='Time zones';

CREATE TABLE IF NOT EXISTS time_zone_name (
  Name char(64) NOT NULL,
  Time_zone_id int unsigned NOT NULL,
  PRIMARY KEY (Name)
) CHARACTER SET utf8 COMMENT='Time zone names';

CREATE TABLE IF NOT EXISTS time_zone_transition (
  Time_zone_id int unsigned NOT NULL,
  Transition_time bigint signed NOT NULL,
  Transition_type_id int unsigned NOT NULL,
  PRIMARY KEY (Time_zone_id, Transition_time)
) CHARACTER SET utf8 COMMENT='Time zone transitions';

CREATE TABLE IF NOT EXISTS time_zone_transition_type (
  Time_zone_id int unsigned NOT NULL,
  Transition_type_id int unsigned NOT NULL,
  Offset int signed NOT NULL default 0,
  Is_DST tinyint unsigned NOT NULL default 0,
  Abbreviation char(8) NOT NULL default '',
  PRIMARY KEY (Time_zone_id, Transition_type_id)
) CHARACTER SET utf8 COMMENT='Time zone transition types';

CREATE TABLE IF NOT EXISTS time_zone_leap_second (
  Transition_time bigint signed NOT NULL,
  Correction int signed NOT NULL,
  PRIMARY KEY (Transition_time)
) CHARACTER SET utf8 COMMENT='Leap seconds information for time zones';

-- Insertar datos básicos para UTC
INSERT IGNORE INTO time_zone (Time_zone_id, Use_leap_seconds) VALUES (1, 'N');
INSERT IGNORE INTO time_zone_name (Name, Time_zone_id) VALUES ('UTC', 1);
INSERT IGNORE INTO time_zone_transition_type (Time_zone_id, Transition_type_id, Offset, Is_DST, Abbreviation) VALUES (1, 0, 0, 0, 'UTC');

-- Insertar datos para America/Bogota
INSERT IGNORE INTO time_zone (Time_zone_id, Use_leap_seconds) VALUES (2, 'N');
INSERT IGNORE INTO time_zone_name (Name, Time_zone_id) VALUES ('America/Bogota', 2);
INSERT IGNORE INTO time_zone_transition_type (Time_zone_id, Transition_type_id, Offset, Is_DST, Abbreviation) VALUES (2, 0, -18000, 0, 'COT');

-- Configurar la zona horaria del servidor a UTC
SET GLOBAL time_zone = '+00:00';
SET time_zone = '+00:00';

-- Verificar la configuración
SELECT @@global.time_zone, @@session.time_zone;

-- Actualizar privilegios
FLUSH PRIVILEGES;