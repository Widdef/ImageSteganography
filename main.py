from imagesteganography.utilities.logger import get_logger
from imagesteganography.utilities.config import get_config
from imagesteganography.UX.gui import run_gui


def main():
    config = get_config()
    log = get_logger()
    log.info("Załadowao config")
    run_gui()
    log.info("Uruchomiono GUI")


if __name__ == "__main__":
    main()