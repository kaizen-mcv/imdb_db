"""Sistema de logging centralizado para IMDb."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import settings


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True,
) -> Path:
    """
    Configura el sistema de logging.

    Args:
        log_level: Nivel de logging
        log_file: Nombre del archivo de log
        console: Si True, muestra logs en consola

    Returns:
        Path al archivo de log creado
    """
    log_dir = settings.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"imdb_{timestamp}.log"

    log_path = log_dir / log_file

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(
        log_path, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    handlers: list[logging.Handler] = [file_handler]

    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers,
        force=True,
    )

    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return log_path


def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger con el nombre especificado."""
    return logging.getLogger(name)


# Logger por defecto del proyecto
logger = get_logger("imdb")
