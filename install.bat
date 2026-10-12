@echo off
REM CODEX - Windows kurulum scripti
REM Kullanim: install.bat  (cift tiklayabilir ya da cmd icinde calistirabilirsiniz)
REM Bu script "codex" komutunu olusturur. Windows buyuk/kucuk harfe duyarsiz
REM oldugu icin Codex ve CODEX de ayni komutu acar.
setlocal

set "REPO_DIR=%~dp0"
if "%REPO_DIR:~-1%"=="\" set "REPO_DIR=%REPO_DIR:~0,-1%"
set "MAIN=%REPO_DIR%\main.py"

if not exist "%MAIN%" (
    echo Error / Hata: main.py not found / bulunamadi: %MAIN%
    exit /b 1
)

REM Gercek Python yolunu bul (Microsoft Store kisayollari yerine)
set "PYEXE="
for /f "delims=" %%i in ('py -c "import sys; print(sys.executable)" 2^>nul') do set "PYEXE=%%i"
if not defined PYEXE (
    for /f "delims=" %%i in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PYEXE=%%i"
)
if not defined PYEXE (
    echo Error / Hata: Python not found / bulunamadi. Install from python.org and
    echo Tick "Add python.exe to PATH" / "Add python.exe to PATH" secenegini isaretleyin.
    exit /b 1
)

set "BIN_DIR=%LOCALAPPDATA%\Codex\bin"
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"

> "%BIN_DIR%\codex.cmd" echo @echo off
>> "%BIN_DIR%\codex.cmd" echo "%PYEXE%" "%MAIN%" %%*

echo Installed / Kuruldu: %BIN_DIR%\codex.cmd
echo Type codex, Codex or CODEX from any folder. / Herhangi bir klasorde codex, Codex ya da CODEX yazin.

echo %PATH% | find /i "%BIN_DIR%" >nul
if errorlevel 1 (
    echo.
    echo Note / Not: %BIN_DIR% is not in PATH. Run this once in PowerShell:
    echo   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";$env:LOCALAPPDATA\Codex\bin", "User")
    echo Then open a new cmd window. / Sonra yeni bir cmd penceresi acin.
)

endlocal
