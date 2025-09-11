@echo on

echo ===============================================
echo Iniciando script de gestión de servicios automáticos
echo Fecha y hora: %date% %time%
echo ===============================================

:: Determinar la ruta del script
SET script_path=%~dp0
SET project_path=%script_path%..

echo Ruta del proyecto: %project_path%

:: Cambiar al directorio del proyecto
cd /d "%project_path%"

echo Directorio actual: %cd%

:: Activar entorno virtual si existe
IF EXIST "%project_path%\venv\Scripts\activate.bat" (
    echo Activando entorno virtual...
    call "%project_path%\venv\Scripts\activate.bat"
) ELSE (
    echo No se encontró entorno virtual.
)

echo Ejecutando comando de Django: python manage.py gestionar_servicios_automaticos

:: Ejecutar el comando de Django y capturar la salida
python manage.py gestionar_servicios_automaticos

IF %ERRORLEVEL% EQU 0 (
    echo Comando ejecutado con éxito.
) ELSE (
    echo Error al ejecutar el comando. Código de error: %ERRORLEVEL%
)

:: Desactivar entorno virtual si fue activado
IF EXIST "%project_path%\venv\Scripts\activate.bat" (
    echo Desactivando entorno virtual...
    call deactivate
)

echo ===============================================
echo Finalizado script de gestión de servicios automáticos
echo Fecha y hora: %date% %time%
echo ===============================================

exit