@echo off
setlocal

REM MdDoc Windows Launcher / Drag & Drop Handler
REM Drop any .md file onto this .bat file to instantly convert to DOCX.

if "%~1"=="" (
    echo ======================================================================
    echo                      MdDoc - Markdown to Beautiful DOCX
    echo ======================================================================
    echo Usage:
    echo   Drag and drop any Markdown file (.md) onto this batch script, OR run:
    echo   mddoc.bat input.md [-o output.docx] [--theme modern^|nordic^|academic^|forest^|corporate]
    echo.
    echo Available themes: modern, nordic, academic, forest, corporate
    echo ======================================================================
    pause
    exit /b 0
)

python "%~dp0mddoc.py" %*

if errorlevel 1 (
    echo.
    echo [!] Conversion encountered an error.
    pause
)
