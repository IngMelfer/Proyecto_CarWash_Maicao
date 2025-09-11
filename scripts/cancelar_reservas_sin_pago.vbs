' Script VBS para ejecutar el script batch en segundo plano
' Este script evita que aparezca una ventana de comando

Option Explicit

Dim WshShell, fso, scriptPath, logPath
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Ruta del script batch a ejecutar
scriptPath = fso.GetParentFolderName(WScript.ScriptFullName) & "\cancelar_reservas_sin_pago.bat"

' Ruta del archivo de log
logPath = fso.GetParentFolderName(WScript.ScriptFullName) & "\logs\cancelar_reservas_" & _
          Year(Now) & Right("0" & Month(Now), 2) & Right("0" & Day(Now), 2) & ".log"

' Crear directorio de logs si no existe
If Not fso.FolderExists(fso.GetParentFolderName(WScript.ScriptFullName) & "\logs") Then
    fso.CreateFolder(fso.GetParentFolderName(WScript.ScriptFullName) & "\logs")
End If

' Ejecutar el script batch en segundo plano y redirigir la salida al archivo de log
WshShell.Run "cmd /c """" & scriptPath & """" > """" & logPath & """" 2>&1", 0, False

Set WshShell = Nothing
Set fso = Nothing