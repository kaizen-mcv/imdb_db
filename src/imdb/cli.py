"""CLI de IMDb con Typer."""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .db import init_db, drop_db, get_session
from .downloader import download_all, download_dataset
from .importer import importar_todo, importar_dataset
from .models import (
    DATASETS, LOAD_ORDER,
    TitleBasics, TitleRatings, NameBasics,
    TitleAkas, TitleCrew, TitleEpisode,
    TitlePrincipals,
)

app = typer.Typer(
    name="imdb",
    help="CLI para datos IMDb Non-Commercial en PostgreSQL",
    no_args_is_help=True,
)
console = Console()


@app.command()
def init(
    drop: bool = typer.Option(
        False, "--drop",
        help="Borrar y recrear tablas",
    ),
):
    """Inicializar base de datos (crear tablas)."""
    console.print(
        "[bold]Inicializando base de datos...[/bold]"
    )
    try:
        if drop:
            if typer.confirm(
                "¿Borrar todas las tablas?"
            ):
                drop_db()
                console.print(
                    "[yellow]Tablas eliminadas.[/yellow]"
                )
            else:
                raise typer.Abort()
        init_db()
        console.print(
            "[green]Base de datos inicializada.[/green]"
        )
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def download(
    dataset: Optional[str] = typer.Option(
        None, "--dataset", "-d",
        help="Dataset especifico (ej: title.basics)",
    ),
    force: bool = typer.Option(
        False, "--force", "-f",
        help="Re-descargar aunque ya exista",
    ),
):
    """Descargar ficheros TSV.gz de IMDb."""
    if dataset:
        if dataset not in DATASETS:
            console.print(
                f"[red]Dataset desconocido: {dataset}"
                f"[/red]"
            )
            console.print(
                f"Disponibles: "
                f"{', '.join(LOAD_ORDER)}"
            )
            raise typer.Exit(1)
        console.print(
            f"[bold]Descargando {dataset}...[/bold]"
        )
        path = download_dataset(dataset, force=force)
        if path:
            console.print(
                f"[green]Descargado: {path}[/green]"
            )
        else:
            console.print(
                "[red]Error en la descarga.[/red]"
            )
            raise typer.Exit(1)
    else:
        console.print(
            "[bold]Descargando todos los datasets..."
            "[/bold]"
        )
        resultados = download_all(force=force)
        console.print(
            f"[green]Descargados: "
            f"{len(resultados)}/{len(LOAD_ORDER)}"
            f"[/green]"
        )


@app.command()
def load(
    dataset: Optional[str] = typer.Option(
        None, "--dataset", "-d",
        help="Dataset especifico (ej: title.basics)",
    ),
    truncate: bool = typer.Option(
        False, "--truncate",
        help="Vaciar tabla antes de importar",
    ),
):
    """Importar TSV.gz a PostgreSQL."""
    if dataset:
        if dataset not in DATASETS:
            console.print(
                f"[red]Dataset desconocido: {dataset}"
                f"[/red]"
            )
            raise typer.Exit(1)
        console.print(
            f"[bold]Importando {dataset}...[/bold]"
        )
        filas = importar_dataset(
            dataset, truncate=truncate
        )
        console.print(
            f"[green]Importadas {filas:,} filas.[/green]"
        )
    else:
        console.print(
            "[bold]Importando todos los datasets..."
            "[/bold]"
        )
        resultados = importar_todo(truncate=truncate)
        table = Table(title="Resultado de importacion")
        table.add_column("Dataset", style="cyan")
        table.add_column(
            "Filas", style="green", justify="right"
        )
        for name, filas in resultados.items():
            table.add_row(name, f"{filas:,}")
        console.print(table)


@app.command()
def status():
    """Mostrar estadisticas de la base de datos."""
    session = get_session()
    try:
        # Conteo de filas por tabla
        modelos = {
            "title_basics": TitleBasics,
            "name_basics": NameBasics,
            "title_akas": TitleAkas,
            "title_crew": TitleCrew,
            "title_episode": TitleEpisode,
            "title_ratings": TitleRatings,
            "title_principals": TitlePrincipals,
        }

        table = Table(title="Estadisticas IMDb")
        table.add_column("Tabla", style="cyan")
        table.add_column(
            "Filas", style="green", justify="right"
        )

        for nombre, modelo in modelos.items():
            count = session.query(modelo).count()
            table.add_row(nombre, f"{count:,}")

        console.print(table)

        # Tamaño de ficheros descargados
        downloads = settings.downloads_dir
        if downloads.exists():
            table2 = Table(
                title="Ficheros descargados"
            )
            table2.add_column(
                "Fichero", style="cyan"
            )
            table2.add_column(
                "Tamaño", style="green", justify="right"
            )
            for f in sorted(downloads.iterdir()):
                if f.is_file():
                    size_mb = f.stat().st_size / (
                        1024 * 1024
                    )
                    table2.add_row(
                        f.name, f"{size_mb:.1f} MB"
                    )
            console.print(table2)

    finally:
        session.close()


# Importar settings aqui para evitar circular
from .config import settings  # noqa: E402


if __name__ == "__main__":
    app()
