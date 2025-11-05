@echo off
title Instalador del Asistente de Voz AGP Andaluz
color 0A
echo.
echo ===============================================
echo     🚀 Instalando Asistente de Voz AGP v4.0 DIOS
echo ===============================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en PATH
    echo Por favor instala Python 3.9 o superior desde python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

REM Crear entorno virtual
echo 📦 Creando entorno virtual...
python -m venv venv
if errorlevel 1 (
    echo ❌ Error creando entorno virtual
    pause
    exit /b 1
)

REM Activar entorno
echo ✅ Activando entorno...
call venv\Scripts\activate.bat

REM Actualizar pip
echo 📦 Actualizando pip...
python -m pip install --upgrade pip --quiet

@echo off
REM Cambia la ruta a la carpeta donde tienes voz_ai
cd /d C:\voz_ai

REM Si tienes un entorno virtual, actívalo
IF EXIST venv (
    call venv\Scripts\activate
)

REM Ejecuta el asistente. Usa 'pythonw' si es GUI y no quieres consola
python archivo.py
REM Alternativa:
REM start "" pythonw archivo.py
