@echo off
::=========================================================================
:: Script para cancelar reservas pendientes sin pago después de 15 minutos
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

cd /d C:\Proyectos_2025\autolavados-plataforma
python manage.py cancelar_reservas_sin_pago > nul 2>&1

REM No mostrar mensaje de finalización