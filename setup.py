import platform
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def run_linux() -> None:
    script = PROJECT_ROOT / "setup_env.sh"
    try:
        subprocess.run(["bash", str(script)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] setup_env.sh zakończył się błędem exit={e.returncode}")
        sys.exit(e.returncode)

def run_windows() -> None:
    script = PROJECT_ROOT / "setup_env.ps1"
    if not script.exists():
        print(f"[!] Brak skryptu: {script}")
        sys.exit(1)

    print("[*] Uruchamiam setup_env.ps1 przez PowerShell...")
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[!] setup_env.ps1 zakończył się błędem exit={e.returncode}")
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