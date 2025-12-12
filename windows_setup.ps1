#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"

$PYTHON_BIN = $env:PYTHON_BIN
if (-not $PYTHON_BIN) { $PYTHON_BIN = "python" }

$VENV_DIR = $env:VENV_DIR
if (-not $VENV_DIR) { $VENV_DIR = "venv" }

Set-Location $PSScriptRoot

$pythonCmd = Get-Command $PYTHON_BIN -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[!] Nie znaleziono Pythona"
    exit 1
}

& $PYTHON_BIN -m venv $VENV_DIR
. ".\$VENV_DIR\Scripts\Activate.ps1"
& $PYTHON_BIN -m pip install --upgrade pip setuptools wheel

if (Test-Path ".\pyproject.toml") {
    pip install -e .
} else {
    Write-Host "[!] Brak pyproject.toml"
}