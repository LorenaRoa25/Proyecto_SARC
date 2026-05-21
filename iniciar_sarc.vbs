Option Explicit

Dim fso, shell, projectDir, appPath, pythonCmd, command

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

projectDir = fso.GetParentFolderName(WScript.ScriptFullName)
appPath = fso.BuildPath(projectDir, "app.py")

ValidateProject

pythonCmd = FindPython()

If pythonCmd = "" Then
  Fail "No se encontro Python instalado o agregado al PATH." & vbCrLf & vbCrLf & _
       "Instale Python 3 desde https://www.python.org/downloads/ y marque Add python.exe to PATH."
End If

If LCase(fso.GetFileName(pythonCmd)) = "py.exe" Or LCase(fso.GetFileName(pythonCmd)) = "pyw.exe" Then
  command = Quote(pythonCmd) & " -3 " & Quote(appPath)
Else
  command = Quote(pythonCmd) & " " & Quote(appPath)
End If

shell.CurrentDirectory = projectDir
shell.Run command, 0, False

Sub ValidateProject()
  If Not fso.FileExists(appPath) Then
    Fail "No se encontro app.py en la carpeta de SARC."
  End If

  If Not fso.FileExists(fso.BuildPath(projectDir, "index.html")) Then
    Fail "No se encontro index.html en la carpeta de SARC."
  End If

  If Not fso.FileExists(fso.BuildPath(projectDir, "shared\js\app.js")) Then
    Fail "La estructura de SARC esta incompleta: falta shared\js\app.js."
  End If

  If Not fso.FileExists(fso.BuildPath(projectDir, "shared\js\firebase-config.js")) Then
    Fail "La estructura de SARC esta incompleta: falta shared\js\firebase-config.js."
  End If
End Sub

Function FindCommand(commandName)
  Dim exec, output, lines

  On Error Resume Next
  Set exec = shell.Exec("%ComSpec% /c where " & commandName)
  If Err.Number <> 0 Then
    Err.Clear
    FindCommand = ""
    On Error GoTo 0
    Exit Function
  End If
  On Error GoTo 0

  Do While exec.Status = 0
    WScript.Sleep 50
  Loop

  output = Trim(exec.StdOut.ReadAll)
  If output = "" Then
    FindCommand = ""
  Else
    lines = Split(output, vbCrLf)
    FindCommand = Trim(lines(0))
  End If
End Function

Function FindPython()
  Dim localAppData, programsDir

  localAppData = shell.ExpandEnvironmentStrings("%LOCALAPPDATA%")
  programsDir = fso.BuildPath(localAppData, "Programs\Python")

  FindPython = FirstExisting(Array( _
    fso.BuildPath(localAppData, "Python\bin\pythonw.exe"), _
    fso.BuildPath(localAppData, "Python\pythoncore-3.14-64\pythonw.exe"), _
    fso.BuildPath(programsDir, "Python314\pythonw.exe"), _
    fso.BuildPath(programsDir, "Python313\pythonw.exe"), _
    fso.BuildPath(programsDir, "Python312\pythonw.exe"), _
    fso.BuildPath(programsDir, "Python311\pythonw.exe") _
  ))

  If FindPython = "" Then FindPython = FindCommand("pythonw.exe")
  If FindPython = "" Then FindPython = FindCommand("pyw.exe")
  If FindPython = "" Then FindPython = FindCommand("python.exe")
  If FindPython = "" Then FindPython = FindCommand("py.exe")
End Function

Function FirstExisting(paths)
  Dim item

  FirstExisting = ""
  For Each item In paths
    If fso.FileExists(item) Then
      FirstExisting = item
      Exit Function
    End If
  Next
End Function

Function Quote(value)
  Quote = Chr(34) & value & Chr(34)
End Function

Sub Fail(message)
  MsgBox message, vbCritical, "SARC"
  WScript.Quit 1
End Sub
