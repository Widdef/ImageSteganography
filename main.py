from src.utilities.logger import get_logger
from src.utilities.config import get_config


def main():
    config = get_config()
    log = get_logger()
    log.info("Załadowao config")


if __name__ == "__main__":
    main()