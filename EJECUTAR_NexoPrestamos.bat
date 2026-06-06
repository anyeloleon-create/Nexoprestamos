@echo off
chcp 65001 > nul
title NexoPréstamos — Launcher
color 0A

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║        NexoPréstamos — Gestor Inteligente                ║
echo  ║        Universidad de Antioquia · 2026-1                 ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

:: Verificar que Python esté instalado
python --version > nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python no está instalado o no está en el PATH.
    echo  Descárgalo de: https://www.python.org/downloads/
    echo  Asegúrate de marcar "Add Python to PATH" al instalar.
    pause
    exit /b 1
)

echo  [OK] Python encontrado.

:: Instalar fpdf2 si no está (para generación de PDF - bonificación)
echo  [INFO] Verificando dependencias opcionales ^(fpdf2^)...
python -c "import fpdf" > nul 2>&1
if errorlevel 1 (
    echo  [INFO] Instalando fpdf2 para generación de PDF...
    pip install fpdf2 --quiet
) else (
    echo  [OK] fpdf2 disponible - se generarán PDFs de bonificación.
)

:: Crear carpeta data si no existe
if not exist "src\data" mkdir "src\data"
if not exist "data" mkdir "data"

echo.
echo  Iniciando NexoPréstamos...
echo  ─────────────────────────────────────────────────────────
echo.

:: Ejecutar el programa
cd /d "%~dp0"
python src/main.py

:: Si hay error
if errorlevel 1 (
    echo.
    echo  [ERROR] El programa terminó con errores.
    pause
)
