' =========================================================================
' Script VBS para ejecutar el comando de cancelación de reservas sin pago de forma silenciosa
' =========================================================================
'
' DESCRIPCIÓN:
' Este script ejecuta el comando Django para cancelar reservas sin pago de forma
' completamente silenciosa, sin mostrar ninguna ventana o interfaz gráfica.
' Está diseñado para ser programado en el Programador de tareas de Windows.
'
' REQUISITOS:
' - Python debe estar instalado y configurado en el PATH del sistema
' - El proyecto Django debe estar correctamente configurado
'
' CONFIGURACIÓN:
' - Ajustar la ruta del proyecto según sea necesario
' - Para cambiar parámetros como el tiempo de espera, modificar strCommand
'
' NOTAS:
' - Para depuración, se puede modificar el valor 0 en objShell.Run a 1 para mostrar ventana
' - Para registrar la ejecución, agregar una línea que escriba en un archivo de log

Option Explicit

Dim objShell, strCommand

' Configurar el comando a ejecutar
strCommand = "python C:\Proyectos_2025\autolavados-plataforma\manage.py cancelar_reservas_sin_pago"

' Crear objeto Shell
Set objShell = CreateObject("WScript.Shell")

' Cambiar al directorio del proyecto
objShell.CurrentDirectory = "C:\Proyectos_2025\autolavados-plataforma"

' Ejecutar el comando sin mostrar ventana (0 = oculto)
objShell.Run strCommand, 0, True

' Liberar el objeto
Set objShell = Nothing