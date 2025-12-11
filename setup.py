import platform
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
LINUX_SCRIPT="linux_setup.sh"
WINDOWS_SCRIPT="windows_setup.ps1"

def run_linux() -> None:
    script = PROJECT_ROOT / LINUX_SCRIPT
    try:
        subprocess.run(["bash", str(script)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] {LINUX_SCRIPT} zakończył się błędem exit={e.returncode}")
        sys.exit(e.returncode)

def run_windows() -> None:
    script = PROJECT_ROOT / WINDOWS_SCRIPT
    if not script.exists():
        print(f"[!] Brak skryptu: {script}")
        sys.exit(1)

    print(f"[*] Uruchamiam {WINDOWS_SCRIPT} przez PowerShell...")
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[!] {WINDOWS_SCRIPT} zakończył się błędem exit={e.returncode}")
        sys.exit(e.returncode)


def main():
    system = platform.system()

    print(f"[*] Wykryty system: {system}")

    if system == "Windows":
        run_windows()
    elif system in ("Linux", "Darwin"):  # macOS = Darwin
        run_linux()
    else:
        print(f"[!] System {system} nie jest obsługiwany.")
        sys.exit(1)

    print("[✓] Konfiguracja zakończona pomyślnie.")


if __name__ == "__main__":
    main()