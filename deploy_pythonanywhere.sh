#!/bin/bash
# ========================================
# SCRIPT DE DESPLIEGUE PARA PYTHONANYWHERE
# ========================================
# 
# Este script automatiza el proceso de despliegue que describes:
# cd ~/Proyecto_CarWash_Maicao 
# git fetch origin 
# git checkout -B main origin/main 
# git reset --hard origin/main 
# git clean -fd 
# workon carwash_env 
# pip install -r requirements.txt
# python manage.py migrate --noinput 
# python manage.py collectstatic --noinput
#
# USO: bash deploy_pythonanywhere.sh
# ========================================

set -e  # Salir si cualquier comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ========================================
# CONFIGURACIÓN
# ========================================
PROJECT_DIR="$HOME/Proyecto_CarWash_Maicao"
VENV_NAME="carwash_env"
BRANCH="main"

log "Iniciando despliegue en PythonAnywhere..."
log "Directorio del proyecto: $PROJECT_DIR"
log "Entorno virtual: $VENV_NAME"
log "Rama: $BRANCH"

# ========================================
# VERIFICACIONES INICIALES
# ========================================
log "Verificando directorio del proyecto..."
if [ ! -d "$PROJECT_DIR" ]; then
    error "El directorio $PROJECT_DIR no existe"
    exit 1
fi

cd "$PROJECT_DIR"
success "Directorio del proyecto encontrado"

# Verificar si es un repositorio git
if [ ! -d ".git" ]; then
    error "No es un repositorio git válido"
    exit 1
fi

# ========================================
# ACTUALIZACIÓN DEL CÓDIGO
# ========================================
log "Obteniendo últimos cambios del repositorio..."
git fetch origin

log "Cambiando a la rama $BRANCH..."
git checkout -B $BRANCH origin/$BRANCH

log "Reseteando a la última versión..."
git reset --hard origin/$BRANCH

log "Limpiando archivos no rastreados..."
git clean -fd

success "Código actualizado correctamente"

# ========================================
# ACTIVACIÓN DEL ENTORNO VIRTUAL
# ========================================
log "Activando entorno virtual $VENV_NAME..."

# Verificar si el entorno virtual existe
if [ ! -d "$HOME/.virtualenvs/$VENV_NAME" ]; then
    error "El entorno virtual $VENV_NAME no existe"
    error "Créalo con: mkvirtualenv --python=/usr/bin/python3.10 $VENV_NAME"
    exit 1
fi

# Activar el entorno virtual
source "$HOME/.virtualenvs/$VENV_NAME/bin/activate"
success "Entorno virtual activado"

# ========================================
# VERIFICACIÓN DEL ARCHIVO .env
# ========================================
log "Verificando archivo de configuración..."
if [ ! -f ".env" ]; then
    warning "Archivo .env no encontrado"
    if [ -f ".env.pythonanywhere" ]; then
        log "Copiando .env.pythonanywhere como .env..."
        cp .env.pythonanywhere .env
        warning "IMPORTANTE: Edita el archivo .env con tus configuraciones reales"
        warning "Ejecuta: nano .env"
    else
        error "No se encontró archivo de configuración"
        exit 1
    fi
else
    success "Archivo .env encontrado"
fi

# ========================================
# INSTALACIÓN DE DEPENDENCIAS
# ========================================
log "Verificando si hay cambios en requirements.txt..."
if [ -f "requirements.txt" ]; then
    log "Instalando/actualizando dependencias..."
    pip install -r requirements.txt
    success "Dependencias instaladas"
else
    warning "No se encontró requirements.txt"
fi

# ========================================
# MIGRACIONES DE BASE DE DATOS
# ========================================
log "Ejecutando migraciones de base de datos..."
python manage.py migrate --noinput
success "Migraciones completadas"

# ========================================
# ARCHIVOS ESTÁTICOS
# ========================================
log "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput
success "Archivos estáticos recolectados"

# ========================================
# VERIFICACIONES POST-DESPLIEGUE
# ========================================
log "Ejecutando verificaciones post-despliegue..."

# Verificar que Django puede importar settings
python -c "import django; django.setup()" 2>/dev/null
if [ $? -eq 0 ]; then
    success "Configuración de Django válida"
else
    error "Error en la configuración de Django"
    exit 1
fi

# Verificar conexión a la base de datos
python manage.py check --database default
if [ $? -eq 0 ]; then
    success "Conexión a base de datos OK"
else
    warning "Problemas con la conexión a la base de datos"
fi

# ========================================
# FINALIZACIÓN
# ========================================
success "¡Despliegue completado exitosamente!"
log "Recuerda:"
log "1. Recargar tu aplicación web en el panel de PythonAnywhere"
log "2. Verificar que el archivo .env tenga las configuraciones correctas"
log "3. Revisar los logs si hay algún problema"

# Mostrar información del commit actual
CURRENT_COMMIT=$(git rev-parse --short HEAD)
COMMIT_MESSAGE=$(git log -1 --pretty=format:"%s")
log "Commit desplegado: $CURRENT_COMMIT - $COMMIT_MESSAGE"

log "Despliegue finalizado en $(date)"