@echo off
REM Script para cancelar reservas vencidas automáticamente
REM Este script debe ser programado para ejecutarse cada 15 minutos

cd /d "C:\Proyectos_2025\Proyecto_CarWash_Maicao"

REM Activar el entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Ejecutar el comando de cancelación de reservas vencidas
python manage.py cancelar_reservas_vencidas

REM Opcional: Registrar la ejecución en un log
echo %date% %time% - Comando cancelar_reservas_vencidas ejecutado >> logs\cancelar_reservas_vencidas.log

pause