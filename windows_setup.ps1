#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"

# Konfiguracja
$PYTHON_BIN = $env:PYTHON_BIN
if (-not $PYTHON_BIN) { $PYTHON_BIN = "python" }

$VENV_DIR = $env:VENV_DIR
if (-not $VENV_DIR) { $VENV_DIR = "venv" }

Write-Host "[*] Sprawdzam, czy dostępny jest $PYTHON_BIN..."

$pythonPath = (Get-Command $PYTHON_BIN -ErrorAction SilentlyContinue)

if (-not $pythonPath) {
    Write-Host "[!] Nie znaleziono $PYTHON_BIN w PATH."
    Write-Host "    Upewnij się, że Python 3.x jest zainstalowany,"
    Write-Host "    albo uruchom skrypt tak:"
    Write-Host "    set PYTHON_BIN=C:\Python311\python.exe"
    Write-Host "    .\windows_env.ps1"
    exit 1
}

Write-Host "[*] Tworzę virtualenv w $VENV_DIR przy użyciu $PYTHON_BIN..."
& $PYTHON_BIN -m venv $VENV_DIR

Write-Host "[*] Aktywuję virtualenv..."
# Uwaga: aktywacja dotyczy TYLKO bieżącej sesji PowerShell
. "$VENV_DIR\Scripts\Activate.ps1"

Write-Host "[*] Aktualizuję pip/setuptools/wheel..."
python -m pip install --upgrade pip setuptools wheel

if (Test-Path "requirements.txt") {
    Write-Host "[*] Instaluję zależności z requirements.txt..."
    pip install -r requirements.txt
}
else {
    Write-Host "[!] Brak requirements.txt — pomijam instalację zależności."
}

Write-Host ""
Write-Host "[✓] Środowisko gotowe."
Write-Host "    Aby z niego korzystać, wykonaj w PowerShell:"
Write-Host "    source ${VENV_DIR}/bin/activate"
