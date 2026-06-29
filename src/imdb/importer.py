"""Importacion masiva de TSV.gz a PostgreSQL via COPY."""

import csv
import gzip
import sys
from pathlib import Path

import psycopg
from psycopg import sql
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TimeElapsedColumn,
)

from .config import settings
from .logger import get_logger
from .models import DATASETS, LOAD_ORDER

# Algunos campos de IMDb superan el limite por defecto del modulo csv
csv.field_size_limit(sys.maxsize)

logger = get_logger(__name__)


def _psycopg_url() -> str:
    """Convierte URL de SQLAlchemy a psycopg3."""
    return settings.db_url.replace("postgresql+psycopg", "postgresql")


def _limpiar_valor(valor: str) -> str | None:
    """Convierte \\N de IMDb a None."""
    return None if valor == "\\N" else valor


def _col(fila: list[str], i: int) -> str:
    """Acceso seguro a columna, devuelve \\N si no existe."""
    return fila[i] if i < len(fila) else "\\N"


def _transformar_title_basics(fila: list[str]) -> tuple:
    """Transforma fila de title.basics.tsv."""
    return (
        fila[0],  # tconst
        _limpiar_valor(_col(fila, 1)),  # title_type
        _limpiar_valor(_col(fila, 2)),  # primary_title
        _limpiar_valor(_col(fila, 3)),  # original_title
        _bool(_col(fila, 4)),  # is_adult
        _int(_col(fila, 5)),  # start_year
        _int(_col(fila, 6)),  # end_year
        _int(_col(fila, 7)),  # runtime_minutes
        _limpiar_valor(_col(fila, 8)),  # genres
    )


def _transformar_name_basics(fila: list[str]) -> tuple:
    """Transforma fila de name.basics.tsv."""
    return (
        fila[0],  # nconst
        _limpiar_valor(_col(fila, 1)),  # primary_name
        _int(_col(fila, 2)),  # birth_year
        _int(_col(fila, 3)),  # death_year
        _limpiar_valor(_col(fila, 4)),  # primary_profession
        _limpiar_valor(_col(fila, 5)),  # known_for_titles
    )


def _transformar_title_akas(fila: list[str]) -> tuple:
    """Transforma fila de title.akas.tsv."""
    return (
        _limpiar_valor(_col(fila, 0)),  # title_id
        _int(_col(fila, 1)),  # ordering
        _limpiar_valor(_col(fila, 2)),  # title
        _limpiar_valor(_col(fila, 3)),  # region
        _limpiar_valor(_col(fila, 4)),  # language
        _limpiar_valor(_col(fila, 5)),  # types
        _limpiar_valor(_col(fila, 6)),  # attributes
        _bool(_col(fila, 7)),  # is_original_title
    )


def _transformar_title_crew(fila: list[str]) -> tuple:
    """Transforma fila de title.crew.tsv."""
    return (
        fila[0],  # tconst
        _limpiar_valor(_col(fila, 1)),  # directors
        _limpiar_valor(_col(fila, 2)),  # writers
    )


def _transformar_title_episode(fila: list[str]) -> tuple:
    """Transforma fila de title.episode.tsv."""
    return (
        fila[0],  # tconst
        _limpiar_valor(_col(fila, 1)),  # parent_tconst
        _int(_col(fila, 2)),  # season_number
        _int(_col(fila, 3)),  # episode_number
    )


def _transformar_title_principals(
    fila: list[str],
) -> tuple:
    """Transforma fila de title.principals.tsv."""
    return (
        _limpiar_valor(_col(fila, 0)),  # tconst
        _int(_col(fila, 1)),  # ordering
        _limpiar_valor(_col(fila, 2)),  # nconst
        _limpiar_valor(_col(fila, 3)),  # category
        _limpiar_valor(_col(fila, 4)),  # job
        _limpiar_valor(_col(fila, 5)),  # characters
    )


def _transformar_title_ratings(fila: list[str]) -> tuple:
    """Transforma fila de title.ratings.tsv."""
    return (
        fila[0],  # tconst
        _float(fila[1]),  # average_rating
        _int(fila[2]),  # num_votes
    )


def _int(valor: str) -> int | None:
    """Convierte a int, \\N a None."""
    if valor == "\\N":
        return None
    try:
        return int(valor)
    except ValueError:
        return None


def _float(valor: str) -> float | None:
    """Convierte a float, \\N a None."""
    if valor == "\\N":
        return None
    try:
        return float(valor)
    except ValueError:
        return None


def _bool(valor: str) -> bool | None:
    """Convierte 0/1 a bool, \\N a None."""
    if valor == "\\N":
        return None
    return valor == "1"


# Mapeo de dataset a funcion de transformacion
TRANSFORMADORES = {
    "title.basics": _transformar_title_basics,
    "name.basics": _transformar_name_basics,
    "title.akas": _transformar_title_akas,
    "title.crew": _transformar_title_crew,
    "title.episode": _transformar_title_episode,
    "title.principals": _transformar_title_principals,
    "title.ratings": _transformar_title_ratings,
}


def _contar_lineas(archivo: Path) -> int:
    """Cuenta lineas de un TSV.gz (para progress bar)."""
    logger.info("Contando filas en %s...", archivo.name)
    count = 0
    with gzip.open(archivo, "rt", encoding="utf-8") as f:
        next(f)  # saltar header
        for _ in f:
            count += 1
    return count


def importar_dataset(
    name: str,
    truncate: bool = False,
) -> int:
    """
    Importa un dataset via COPY de PostgreSQL.

    Args:
        name: Nombre del dataset
        truncate: Vaciar tabla antes de importar

    Returns:
        Numero de filas importadas
    """
    if name not in DATASETS:
        logger.error("Dataset desconocido: %s", name)
        return 0

    info = DATASETS[name]
    archivo = settings.downloads_dir / info["url"]

    if not archivo.exists():
        logger.error(
            "Fichero no encontrado: %s. Ejecuta 'imdb download' primero.",
            archivo,
        )
        return 0

    transformar = TRANSFORMADORES[name]
    tabla = info["table"]
    columnas = info["columns"]

    # Contar filas para progress bar
    total = _contar_lineas(archivo)
    logger.info(
        "Importando %s (%d filas) a tabla %s",
        name,
        total,
        tabla,
    )

    conn_url = _psycopg_url()
    filas_ok = 0

    with psycopg.connect(conn_url) as conn:
        with conn.cursor() as cur:
            if truncate:
                cur.execute(
                    sql.SQL("TRUNCATE TABLE {} CASCADE").format(
                        sql.Identifier(tabla)
                    )
                )
                logger.info("Tabla %s vaciada", tabla)

            # COPY con streaming
            copy_sql = sql.SQL("COPY {} ({}) FROM STDIN").format(
                sql.Identifier(tabla),
                sql.SQL(", ").join(map(sql.Identifier, columnas)),
            )

            progress = Progress(
                SpinnerColumn(),
                "[progress.description]{task.description}",
                BarColumn(),
                MofNCompleteColumn(),
                TimeElapsedColumn(),
            )

            with progress:
                task = progress.add_task(
                    f"[cyan]{tabla}",
                    total=total,
                )
                with cur.copy(copy_sql) as copy:
                    with gzip.open(archivo, "rt", encoding="utf-8") as f:
                        reader = csv.reader(f, delimiter="\t")
                        next(reader)  # saltar header
                        for fila in reader:
                            registro = transformar(fila)
                            copy.write_row(registro)
                            filas_ok += 1
                            if filas_ok % 50_000 == 0:
                                progress.update(
                                    task,
                                    completed=filas_ok,
                                )
                    # Actualizar al final
                    progress.update(task, completed=filas_ok)

        conn.commit()

    logger.info("Importadas %d filas en %s", filas_ok, tabla)
    return filas_ok


def importar_todo(truncate: bool = False) -> dict[str, int]:
    """
    Importa todos los datasets en orden.

    Returns:
        Dict con nombre -> filas importadas
    """
    resultados: dict[str, int] = {}
    for name in LOAD_ORDER:
        filas = importar_dataset(name, truncate=truncate)
        resultados[name] = filas
    return resultados
