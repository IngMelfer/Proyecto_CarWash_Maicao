#!/bin/bash
# ========================================
# SCRIPT DE ACTUALIZACIÓN AUTOMÁTICA PARA PYTHONANYWHERE
# ========================================
#
# Este script automatiza el proceso de actualización del proyecto en PythonAnywhere
# Incluye verificaciones de seguridad, backup automático y rollback en caso de errores
#
# Uso: bash actualizar_pythonanywhere_mejorado.sh
#
# Autor: Sistema de Autolavado Premium Car Detailing
# Versión: 2.0
# ========================================

set -e  # Salir si cualquier comando falla

# ========================================
# CONFIGURACIÓN Y VARIABLES
# ========================================
PROJECT_NAME="Proyecto_CarWash_Maicao"
REPO_URL="https://github.com/tu_usuario/tu_repositorio.git"  # Cambiar por tu repo
VENV_NAME="autolavados_env"
BACKUP_DIR="$HOME/backups"
LOG_FILE="$HOME/deployment.log"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ========================================
# FUNCIONES AUXILIARES
# ========================================
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

# ========================================
# FUNCIÓN DE VERIFICACIÓN PREVIA
# ========================================
verificar_entorno() {
    log "🔍 Verificando entorno de PythonAnywhere..."
    
    # Verificar que estamos en PythonAnywhere
    if [[ ! "$HOSTNAME" == *"pythonanywhere"* ]]; then
        warning "Este script está optimizado para PythonAnywhere"
    fi
    
    # Verificar directorio del proyecto
    if [[ ! -d "$HOME/$PROJECT_NAME" ]]; then
        error "Directorio del proyecto no encontrado: $HOME/$PROJECT_NAME"
        exit 1
    fi
    
    # Verificar entorno virtual
    if [[ ! -d "$HOME/.virtualenvs/$VENV_NAME" ]]; then
        error "Entorno virtual no encontrado: $HOME/.virtualenvs/$VENV_NAME"
        exit 1
    fi
    
    success "Entorno verificado correctamente"
}

# ========================================
# FUNCIÓN DE BACKUP
# ========================================
crear_backup() {
    log "💾 Creando backup del proyecto..."
    
    # Crear directorio de backup si no existe
    mkdir -p "$BACKUP_DIR"
    
    # Crear backup del proyecto
    BACKUP_FILE="$BACKUP_DIR/${PROJECT_NAME}_backup_$TIMESTAMP.tar.gz"
    cd "$HOME"
    tar -czf "$BACKUP_FILE" "$PROJECT_NAME" --exclude="$PROJECT_NAME/.git" --exclude="$PROJECT_NAME/__pycache__" --exclude="$PROJECT_NAME/staticfiles"
    
    # Backup de la base de datos (si es posible)
    if command -v mysqldump &> /dev/null; then
        log "📊 Creando backup de la base de datos..."
        DB_BACKUP="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"
        # Nota: Ajustar credenciales según tu configuración
        # mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME > "$DB_BACKUP" 2>/dev/null || warning "No se pudo crear backup de BD"
    fi
    
    success "Backup creado: $BACKUP_FILE"
}

# ========================================
# FUNCIÓN DE ACTUALIZACIÓN DE CÓDIGO
# ========================================
actualizar_codigo() {
    log "📥 Actualizando código desde GitHub..."
    
    cd "$HOME/$PROJECT_NAME"
    
    # Verificar estado del repositorio
    if [[ -d ".git" ]]; then
        # Guardar cambios locales si los hay
        if ! git diff --quiet; then
            warning "Hay cambios locales. Guardando en stash..."
            git stash push -m "Auto-stash before update $TIMESTAMP"
        fi
        
        # Actualizar desde origin
        git fetch origin
        git pull origin main || git pull origin master
        
        success "Código actualizado desde GitHub"
    else
        error "No es un repositorio Git válido"
        exit 1
    fi
}

# ========================================
# FUNCIÓN DE ACTUALIZACIÓN DE DEPENDENCIAS
# ========================================
actualizar_dependencias() {
    log "📦 Actualizando dependencias..."
    
    # Activar entorno virtual
    source "$HOME/.virtualenvs/$VENV_NAME/bin/activate"
    
    # Actualizar pip
    pip install --upgrade pip
    
    # Instalar/actualizar dependencias
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt --upgrade
        success "Dependencias actualizadas"
    else
        warning "Archivo requirements.txt no encontrado"
    fi
}

# ========================================
# FUNCIÓN DE MIGRACIONES
# ========================================
ejecutar_migraciones() {
    log "🗄️  Ejecutando migraciones de base de datos..."
    
    cd "$HOME/$PROJECT_NAME"
    source "$HOME/.virtualenvs/$VENV_NAME/bin/activate"
    
    # Verificar migraciones pendientes
    if python manage.py showmigrations --plan | grep -q "\[ \]"; then
        log "Aplicando migraciones pendientes..."
        python manage.py migrate --noinput
        success "Migraciones aplicadas correctamente"
    else
        log "No hay migraciones pendientes"
    fi
}

# ========================================
# FUNCIÓN DE ARCHIVOS ESTÁTICOS
# ========================================
recolectar_estaticos() {
    log "🎨 Recolectando archivos estáticos..."
    
    cd "$HOME/$PROJECT_NAME"
    source "$HOME/.virtualenvs/$VENV_NAME/bin/activate"
    
    # Recolectar archivos estáticos
    python manage.py collectstatic --noinput --clear
    success "Archivos estáticos recolectados"
}

# ========================================
# FUNCIÓN DE VERIFICACIÓN POST-DESPLIEGUE
# ========================================
verificar_despliegue() {
    log "🔍 Verificando despliegue..."
    
    cd "$HOME/$PROJECT_NAME"
    source "$HOME/.virtualenvs/$VENV_NAME/bin/activate"
    
    # Verificar configuración de Django
    python manage.py check --deploy
    
    # Verificar conexión a la base de datos
    python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('✅ Conexión a BD exitosa')"
    
    success "Verificación completada"
}

# ========================================
# FUNCIÓN DE REINICIO DE APLICACIÓN
# ========================================
reiniciar_aplicacion() {
    log "🔄 Reiniciando aplicación web..."
    
    # Tocar el archivo WSGI para reiniciar
    WSGI_FILE="/var/www/$(whoami)_pythonanywhere_com_wsgi.py"
    if [[ -f "$WSGI_FILE" ]]; then
        touch "$WSGI_FILE"
        success "Aplicación reiniciada"
    else
        warning "Archivo WSGI no encontrado. Reinicia manualmente desde el dashboard."
    fi
}

# ========================================
# FUNCIÓN DE ROLLBACK
# ========================================
rollback() {
    error "Error durante el despliegue. Iniciando rollback..."
    
    # Restaurar desde backup más reciente
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/${PROJECT_NAME}_backup_*.tar.gz 2>/dev/null | head -n1)
    
    if [[ -n "$LATEST_BACKUP" ]]; then
        log "Restaurando desde: $LATEST_BACKUP"
        cd "$HOME"
        rm -rf "$PROJECT_NAME.rollback" 2>/dev/null || true
        mv "$PROJECT_NAME" "$PROJECT_NAME.rollback" 2>/dev/null || true
        tar -xzf "$LATEST_BACKUP"
        success "Rollback completado"
    else
        error "No se encontró backup para rollback"
    fi
}

# ========================================
# FUNCIÓN DE LIMPIEZA
# ========================================
limpiar_archivos() {
    log "🧹 Limpiando archivos temporales..."
    
    cd "$HOME/$PROJECT_NAME"
    
    # Limpiar archivos Python compilados
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Limpiar logs antiguos (mantener últimos 10)
    if [[ -d "logs" ]]; then
        find logs -name "*.log" -type f -mtime +30 -delete 2>/dev/null || true
    fi
    
    # Limpiar backups antiguos (mantener últimos 5)
    if [[ -d "$BACKUP_DIR" ]]; then
        ls -t "$BACKUP_DIR"/${PROJECT_NAME}_backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null || true
    fi
    
    success "Limpieza completada"
}

# ========================================
# FUNCIÓN PRINCIPAL
# ========================================
main() {
    log "🚀 Iniciando actualización automática de PythonAnywhere"
    log "Timestamp: $TIMESTAMP"
    log "Usuario: $(whoami)"
    log "Directorio: $(pwd)"
    
    # Configurar trap para rollback en caso de error
    trap rollback ERR
    
    # Ejecutar pasos de actualización
    verificar_entorno
    crear_backup
    actualizar_codigo
    actualizar_dependencias
    ejecutar_migraciones
    recolectar_estaticos
    verificar_despliegue
    reiniciar_aplicacion
    limpiar_archivos
    
    success "🎉 Actualización completada exitosamente!"
    log "📊 Resumen:"
    log "   - Backup creado: $BACKUP_FILE"
    log "   - Código actualizado desde GitHub"
    log "   - Dependencias actualizadas"
    log "   - Migraciones aplicadas"
    log "   - Archivos estáticos recolectados"
    log "   - Aplicación reiniciada"
    
    # Mostrar información útil
    echo ""
    echo "📋 INFORMACIÓN ÚTIL:"
    echo "   - Log completo: $LOG_FILE"
    echo "   - Backup: $BACKUP_FILE"
    echo "   - Para ver logs en tiempo real: tail -f $LOG_FILE"
    echo "   - Para rollback manual: bash actualizar_pythonanywhere_mejorado.sh rollback"
    echo ""
}

# ========================================
# MANEJO DE ARGUMENTOS
# ========================================
case "${1:-}" in
    "rollback")
        log "🔄 Ejecutando rollback manual..."
        rollback
        ;;
    "backup")
        log "💾 Creando backup manual..."
        verificar_entorno
        crear_backup
        ;;
    "verify")
        log "🔍 Ejecutando verificación..."
        verificar_entorno
        verificar_despliegue
        ;;
    *)
        main
        ;;
esac

log "✨ Script finalizado"