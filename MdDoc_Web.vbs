' MdDoc Web Studio Silent Launcher (No Terminal Window)
' Double-click this file to launch the Web UI in your browser without any command prompt.

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strCurDir = fso.GetParentFolderName(WScript.ScriptFullName)

pythonwPath = WshShell.ExpandEnvironmentStrings("%USERPROFILE%") & "\miniconda3\pythonw.exe"
If Not fso.FileExists(pythonwPath) Then
    If fso.FileExists("C:\Users\ilias\miniconda3\pythonw.exe") Then
        pythonwPath = "C:\Users\ilias\miniconda3\pythonw.exe"
    Else
        pythonwPath = "pythonw"
    End If
End If

WshShell.Run """" & pythonwPath & """ """ & strCurDir & "\mddoc\web_server.py""", 0, False
