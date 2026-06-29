"""Descarga de ficheros TSV.gz de IMDb."""

from pathlib import Path

import requests
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from .config import settings
from .logger import get_logger
from .models import DATASETS, LOAD_ORDER

logger = get_logger(__name__)

BASE_URL = "https://datasets.imdbws.com/"
CHUNK_SIZE = 1024 * 64  # 64 KB


def _get_remote_size(url: str) -> int | None:
    """Obtiene el tamaño remoto con HEAD request."""
    try:
        resp = requests.head(url, timeout=10)
        resp.raise_for_status()
        length = resp.headers.get("Content-Length")
        return int(length) if length else None
    except requests.RequestException:
        return None


def download_dataset(
    name: str,
    force: bool = False,
) -> Path | None:
    """
    Descarga un dataset de IMDb.

    Args:
        name: Nombre del dataset (ej: 'title.basics')
        force: Re-descargar aunque ya exista

    Returns:
        Path al fichero descargado o None si error
    """
    if name not in DATASETS:
        logger.error("Dataset desconocido: %s", name)
        return None

    info = DATASETS[name]
    url = BASE_URL + info["url"]
    dest = settings.downloads_dir / info["url"]
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Comprobar si ya existe y tiene el mismo tamaño
    if not force and dest.exists():
        remote_size = _get_remote_size(url)
        local_size = dest.stat().st_size
        if remote_size and local_size == remote_size:
            logger.info(
                "Saltando %s (ya descargado, %d MB)",
                name,
                local_size // (1024 * 1024),
            )
            return dest

    logger.info("Descargando %s desde %s", name, url)

    try:
        resp = requests.get(url, stream=True, timeout=30)
        resp.raise_for_status()
        total = int(resp.headers.get("Content-Length", 0))

        progress = Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
        )

        with progress:
            task = progress.add_task(f"[cyan]{info['url']}", total=total)
            with open(dest, "wb") as f:
                for chunk in resp.iter_content(CHUNK_SIZE):
                    f.write(chunk)
                    progress.update(task, advance=len(chunk))

        size_mb = dest.stat().st_size / (1024 * 1024)
        logger.info("Descargado %s (%.1f MB)", name, size_mb)
        return dest

    except requests.RequestException as e:
        logger.error("Error descargando %s: %s", name, e)
        # Borrar fichero parcial
        if dest.exists():
            dest.unlink()
        return None


def download_all(force: bool = False) -> dict[str, Path]:
    """
    Descarga todos los datasets configurados.

    Returns:
        Dict con nombre -> path de los descargados
    """
    resultados: dict[str, Path] = {}
    for name in LOAD_ORDER:
        path = download_dataset(name, force=force)
        if path:
            resultados[name] = path
    return resultados
