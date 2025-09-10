@echo off
REM Script para cancelar reservas pendientes sin pago después de 15 minutos
REM Este archivo debe ser programado para ejecutarse periódicamente (por ejemplo, cada 5 minutos)

cd C:\Proyectos_2025\autolavados-plataforma
python manage.py cancelar_reservas_sin_pago

echo Cancelación de reservas sin pago completada