Set WshShell = CreateObject("WScript.Shell")

' Cambiar al directorio del proyecto
WshShell.CurrentDirectory = "C:\Proyectos_2025\Proyecto_CarWash_Maicao"

' Ejecutar el comando de cancelación de reservas vencidas de forma silenciosa
' El parámetro 0 hace que se ejecute sin mostrar ventana
WshShell.Run "cmd /c python manage.py cancelar_reservas_vencidas", 0, True

' Opcional: Registrar la ejecución en un log
Dim fso, logFile, currentDateTime
Set fso = CreateObject("Scripting.FileSystemObject")
currentDateTime = Now()

' Crear directorio de logs si no existe
If Not fso.FolderExists("logs") Then
    fso.CreateFolder("logs")
End If

' Escribir al archivo de log
Set logFile = fso.OpenTextFile("logs\cancelar_reservas_vencidas.log", 8, True)
logFile.WriteLine(currentDateTime & " - Comando cancelar_reservas_vencidas ejecutado silenciosamente")
logFile.Close