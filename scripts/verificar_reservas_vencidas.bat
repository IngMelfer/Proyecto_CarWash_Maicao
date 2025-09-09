@echo off
REM Script para verificar reservas vencidas y marcarlas como incumplidas
REM Este archivo debe ser programado para ejecutarse periódicamente (por ejemplo, cada hora)

cd C:\Proyectos_2025\autolavados-plataforma
python manage.py verificar_reservas_vencidas

echo Verificación de reservas vencidas completada