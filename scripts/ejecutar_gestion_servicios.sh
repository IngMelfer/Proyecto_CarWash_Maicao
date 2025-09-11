#!/bin/bash
# Script para ejecutar el comando de gestión automática de servicios en entornos Linux/Unix
# Este script debe ser programado para ejecutarse cada 5 minutos mediante cron

# Registrar inicio de ejecución
echo "Ejecutando gestión automática de servicios - $(date)"

# Determinar la ruta del script y cambiar al directorio del proyecto
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="${SCRIPT_DIR}/.."
cd "${PROJECT_DIR}"

# Crear directorio de logs si no existe
mkdir -p "${SCRIPT_DIR}/logs"

# Definir archivo de log
LOG_FILE="${SCRIPT_DIR}/logs/gestion_servicios_$(date +%Y%m%d).log"

# Activar el entorno virtual si existe
if [ -f "${PROJECT_DIR}/venv/bin/activate" ]; then
    source "${PROJECT_DIR}/venv/bin/activate"
elif [ -f "${PROJECT_DIR}/env/bin/activate" ]; then
    source "${PROJECT_DIR}/env/bin/activate"
elif [ -f "${PROJECT_DIR}/.venv/bin/activate" ]; then
    source "${PROJECT_DIR}/.venv/bin/activate"
fi

# Ejecutar el comando de Django para gestionar servicios automáticos
python manage.py gestionar_servicios_automaticos

# Registrar finalización
echo "Gestión de servicios completada - $(date)"

# Desactivar el entorno virtual si fue activado
if [ -n "${VIRTUAL_ENV}" ]; then
    deactivate
fi