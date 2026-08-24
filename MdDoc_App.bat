@echo off
REM Launcher for MdDoc Desktop GUI Window
REM Starts pythonw in detached background and closes instantly.

if exist "%USERPROFILE%\miniconda3\pythonw.exe" (
    start "" "%USERPROFILE%\miniconda3\pythonw.exe" "%~dp0mddoc\gui.py"
) else if exist "C:\Users\ilias\miniconda3\pythonw.exe" (
    start "" "C:\Users\ilias\miniconda3\pythonw.exe" "%~dp0mddoc\gui.py"
) else (
    start "" pythonw "%~dp0mddoc\gui.py"
)
exit
