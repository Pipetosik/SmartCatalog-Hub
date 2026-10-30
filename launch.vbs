Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
currDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = currDir
WshShell.Run "pythonw.exe """ & currDir & "\app.py""", 0, False
