@echo off
::=========================================================================
:: Script para cancelar reservas pendientes sin pago después de 5 minutos
::=========================================================================
::
:: DESCRIPCIÓN:
:: Este script ejecuta el comando Django para cancelar reservas sin pago
:: redirigiendo la salida a nul para minimizar la interacción con el usuario.
::
:: CONFIGURACIÓN:
:: - Debe ser programado para ejecutarse periódicamente (cada 5 minutos recomendado)
:: - Ajustar la ruta del proyecto según sea necesario
::
:: NOTAS:
:: - Para ver la salida, eliminar la redirección "> nul 2>&1"
:: - Para cambiar parámetros, agregar opciones al comando (--minutos=30, --dry-run)

REM Determinar la ruta del script y cambiar al directorio del proyecto
SET SCRIPT_DIR=%~dp0
SET PROJECT_DIR=%SCRIPT_DIR%..
cd /d %PROJECT_DIR%

REM Activar el entorno virtual si existe
IF EXIST "%PROJECT_DIR%\venv\Scripts\activate.bat" (
    call "%PROJECT_DIR%\venv\Scripts\activate.bat"
) ELSE IF EXIST "%PROJECT_DIR%\env\Scripts\activate.bat" (
    call "%PROJECT_DIR%\env\Scripts\activate.bat"
) ELSE IF EXIST "%PROJECT_DIR%\.venv\Scripts\activate.bat" (
    call "%PROJECT_DIR%\.venv\Scripts\activate.bat"
)

python manage.py cancelar_reservas_sin_pago > nul 2>&1

REM Desactivar el entorno virtual si fue activado
IF EXIST "%PROJECT_DIR%\venv\Scripts\deactivate.bat" (
    call deactivate
) ELSE IF EXIST "%PROJECT_DIR%\env\Scripts\deactivate.bat" (
    call deactivate
) ELSE IF EXIST "%PROJECT_DIR%\.venv\Scripts\deactivate.bat" (
    call deactivate
)

exit