' Script VBS para ejecutar el script batch en segundo plano
' Este script evita que aparezca una ventana de comando

Option Explicit

Dim WshShell, fso, scriptPath, logPath, logFolder, currentDate, cmd
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Obtener fecha actual para el nombre del archivo de log
currentDate = Year(Now) & Right("0" & Month(Now), 2) & Right("0" & Day(Now), 2)

' Ruta del script batch a ejecutar
scriptPath = fso.GetParentFolderName(WScript.ScriptFullName) & "\ejecutar_gestion_servicios.bat"

' Crear directorio de logs si no existe
logFolder = fso.GetParentFolderName(WScript.ScriptFullName) & "\logs"
If Not fso.FolderExists(logFolder) Then
    fso.CreateFolder(logFolder)
End If

' Ruta del archivo de log
logPath = logFolder & "\gestion_servicios_" & currentDate & ".log"

' Crear un archivo de log vacío o añadir una línea si ya existe
Dim logFile
If Not fso.FileExists(logPath) Then
    Set logFile = fso.CreateTextFile(logPath, True)
Else
    Set logFile = fso.OpenTextFile(logPath, 8, True) ' 8 = ForAppending
End If
logFile.WriteLine "===== Ejecución iniciada: " & Now & " ====="
logFile.Close

' Escribir en el log que se va a ejecutar el comando
Set logFile = fso.OpenTextFile(logPath, 8, True) ' 8 = ForAppending
logFile.WriteLine "===== Ejecutando script batch: " & Now & " ====="
logFile.Close

' Ejecutar el comando directamente con redirección de salida
Dim execCmd
execCmd = "cmd.exe /c call """ & scriptPath & """ >> """ & logPath & """ 2>&1"

' Escribir el comando en el log para depuración
Set logFile = fso.OpenTextFile(logPath, 8, True)
logFile.WriteLine "Comando ejecutado: " & execCmd
logFile.Close

' Ejecutar el comando y esperar a que termine
WshShell.Run execCmd, 0, True

Set logFile = Nothing
Set WshShell = Nothing
Set fso = Nothing