' Script VBS para ejecutar el batch de cancelación de reservas sin mostrar ventana
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "C:\Proyectos_2025\autolavados-plataforma\scripts\cancelar_reservas_sin_pago.bat", 0, True
Set WshShell = Nothing