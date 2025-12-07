#!/usr/bin/env bash
set -e

# Konfiguracja
PYTHON_BIN=${PYTHON_BIN:-python3.14}
VENV_DIR=${VENV_DIR:-venv}

echo "[*] Sprawdzam, czy dostępny jest ${PYTHON_BIN}..."

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "[!] Nie znaleziono ${PYTHON_BIN} w PATH."
  echo "    Zainstaluj Python 3.11 (np. python3.11, python311),"
  echo "    albo uruchom ten skrypt z ustawioną zmienną PYTHON_BIN, np.:"
  echo "    PYTHON_BIN=/ścieżka/do/python3.11 ./linux_setup.sh"
  exit 1
fi

echo "[*] Tworzę virtualenv w ${VENV_DIR} przy użyciu ${PYTHON_BIN}..."
"${PYTHON_BIN}" -m venv "${VENV_DIR}"

echo "[*] Aktywuję virtualenv..."
# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"

echo "[*] Aktualizuję pip/setuptools/wheel..."
python -m pip install --upgrade pip setuptools wheel

echo "[*] Instaluję zależności z requirements.txt..."
pip install -r requirements.txt

echo
echo "[✓] Środowisko gotowe."
echo "    Aby z niego korzystać, wykonaj:"
echo "    source ${VENV_DIR}/bin/activate"