#!/bin/bash
# NexoPréstamos — Launcher para Mac/Linux
# Doble clic o ejecutar: bash EJECUTAR_NexoPrestamos.sh

clear
echo ""
echo "  ╔══════════════════════════════════════════════════════════╗"
echo "  ║        NexoPréstamos — Gestor Inteligente                ║"
echo "  ║        Universidad de Antioquia · 2026-1                 ║"
echo "  ╚══════════════════════════════════════════════════════════╝"
echo ""

# Detectar Python 3
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "  [ERROR] Python no está instalado."
    echo "  Instálalo con: sudo apt install python3  (Linux)"
    echo "              o: brew install python3       (Mac)"
    read -p "  Presiona ENTER para cerrar..."
    exit 1
fi

echo "  [OK] Python encontrado: $($PYTHON --version)"

# Instalar fpdf2 si no está
$PYTHON -c "import fpdf" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  [INFO] Instalando fpdf2 para generación de PDF..."
    pip3 install fpdf2 --quiet 2>/dev/null || pip install fpdf2 --quiet 2>/dev/null
else
    echo "  [OK] fpdf2 disponible - se generarán PDFs de bonificación."
fi

# Crear carpeta data si no existe
mkdir -p "$(dirname "$0")/data"
mkdir -p "$(dirname "$0")/src/data"

echo ""
echo "  Iniciando NexoPréstamos..."
echo "  ─────────────────────────────────────────────────────────"
echo ""

# Cambiar al directorio del script y ejecutar
cd "$(dirname "$0")"
$PYTHON src/main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "  [ERROR] El programa terminó con errores."
    read -p "  Presiona ENTER para cerrar..."
fi
