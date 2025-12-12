import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from utilities.config import get_config

class AppLogger:
    """
    Logger aplikacyjny z dwoma kanałami:
    - konsola
    - plik

    Domyślnie loguje do obu.
    """

    def __init__(
        self,
        aplication_name: str = "App",
        log_dir: str | Path = "logs",
        sub_dir: str | Path = None,
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
    ):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if not isinstance(log_dir, (str, Path)):
            raise TypeError("log_dir must be Path or str")
        
        log_dir = Path(log_dir)

        if sub_dir is not None:
            if not isinstance(sub_dir, (str, Path)):
                raise TypeError("sub_dir must be Path or str or None")
            log_dir = log_dir / sub_dir
 
        log_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = log_dir / f"{aplication_name}_{timestamp}.log"

        # --- logger konsolowy ---
        self._console_logger = logging.getLogger(f"{aplication_name}.console")
        if not self._console_logger.handlers:
            self._console_logger.setLevel(console_level)
            ch = logging.StreamHandler()
            ch.setLevel(console_level)
            fmt = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            ch.setFormatter(fmt)
            self._console_logger.addHandler(ch)
            self._console_logger.propagate = False

        # --- logger plikowy ---
        self._file_logger = logging.getLogger(f"{aplication_name}.file")
        if not self._file_logger.handlers:
            self._file_logger.setLevel(file_level)
            fh = logging.FileHandler(self.log_file, encoding="utf-8")
            fh.setLevel(file_level)
            fmt = logging.Formatter(
                "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            fh.setFormatter(fmt)
            self._file_logger.addHandler(fh)
            self._file_logger.propagate = False

    # --- wewnętrzna pomocnicza ---

    def _log(
        self,
        level: int,
        msg: str,
        *args,
        console: bool = True,
        file: bool = True,
        **kwargs,
    ) -> None:
        if console:
            self._console_logger.log(level, msg, *args, **kwargs)
        if file:
            self._file_logger.log(level, msg, *args, **kwargs)

    # --- publiczne metody ---

    # log do obu (domyślnie)
    def debug(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.CRITICAL, msg, *args, **kwargs)

    # warianty tylko konsola / tylko plik

    def info_console(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.INFO, msg, *args, console=True, file=False, **kwargs)

    def info_file(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.INFO, msg, *args, console=False, file=True, **kwargs)

    def error_console(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.ERROR, msg, *args, console=True, file=False, **kwargs)

    def error_file(self, msg: str, *args, **kwargs) -> None:
        self._log(logging.ERROR, msg, *args, console=False, file=True, **kwargs)


_logger: Optional[AppLogger] = None


def get_logger(dir:str = None) -> AppLogger:
    global _logger
    if _logger is None:
        _logger = AppLogger(log_dir=get_config().get("DIRS","LOGS"), sub_dir=dir)
    return _logger