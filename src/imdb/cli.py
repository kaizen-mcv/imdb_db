"""CLI de IMDb con Typer."""

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .config import settings
from .db import drop_db, get_session, init_db
from .downloader import download_all, download_dataset
from .importer import importar_dataset, importar_todo
from .logger import setup_logging
from .models import (
    DATASETS,
    LOAD_ORDER,
    NameBasics,
    TitleAkas,
    TitleBasics,
    TitleCrew,
    TitleEpisode,
    TitlePrincipals,
    TitleRatings,
)

app = typer.Typer(
    name="imdb",
    help="CLI para datos IMDb Non-Commercial en PostgreSQL",
    no_args_is_help=True,
)
console = Console()


def _version_callback(value: bool):
    if value:
        console.print(f"imdb {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Logging DEBUG en consola y fichero",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Mostrar version y salir",
    ),
):
    """Punto de entrada del CLI."""
    setup_logging(log_level="DEBUG" if verbose else "INFO")


@app.command()
def init(
    drop: bool = typer.Option(
        False,
        "--drop",
        help="Borrar y recrear tablas",
    ),
):
    """Inicializar base de datos (crear tablas)."""
    console.print("[bold]Inicializando base de datos...[/bold]")
    if drop:
        if not typer.confirm("¿Borrar todas las tablas?"):
            raise typer.Abort()
        drop_db()
        console.print("[yellow]Tablas eliminadas.[/yellow]")
    init_db()
    console.print("[green]Base de datos inicializada.[/green]")


@app.command()
def download(
    dataset: str | None = typer.Option(
        None,
        "--dataset",
        "-d",
        help="Dataset especifico (ej: title.basics)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Re-descargar aunque ya exista",
    ),
):
    """Descargar ficheros TSV.gz de IMDb."""
    if dataset:
        if dataset not in DATASETS:
            console.print(f"[red]Dataset desconocido: {dataset}[/red]")
            console.print(f"Disponibles: {', '.join(LOAD_ORDER)}")
            raise typer.Exit(1)
        console.print(f"[bold]Descargando {dataset}...[/bold]")
        path = download_dataset(dataset, force=force)
        if path:
            console.print(f"[green]Descargado: {path}[/green]")
        else:
            console.print("[red]Error en la descarga.[/red]")
            raise typer.Exit(1)
    else:
        console.print("[bold]Descargando todos los datasets...[/bold]")
        resultados = download_all(force=force)
        console.print(
            f"[green]Descargados: {len(resultados)}/{len(LOAD_ORDER)}[/green]"
        )


@app.command()
def load(
    dataset: str | None = typer.Option(
        None,
        "--dataset",
        "-d",
        help="Dataset especifico (ej: title.basics)",
    ),
    truncate: bool = typer.Option(
        False,
        "--truncate",
        help="Vaciar tabla antes de importar",
    ),
):
    """Importar TSV.gz a PostgreSQL."""
    if dataset:
        if dataset not in DATASETS:
            console.print(f"[red]Dataset desconocido: {dataset}[/red]")
            raise typer.Exit(1)
        console.print(f"[bold]Importando {dataset}...[/bold]")
        filas = importar_dataset(dataset, truncate=truncate)
        console.print(f"[green]Importadas {filas:,} filas.[/green]")
        return

    console.print("[bold]Importando todos los datasets...[/bold]")
    resultados = importar_todo(truncate=truncate)
    table = Table(title="Resultado de importacion")
    table.add_column("Dataset", style="cyan")
    table.add_column("Filas", style="green", justify="right")
    for name, filas in resultados.items():
        table.add_row(name, f"{filas:,}")
    console.print(table)


@app.command()
def status():
    """Mostrar estadisticas de la base de datos."""
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
    table.add_column("Filas", style="green", justify="right")

    with get_session() as session:
        for nombre, modelo in modelos.items():
            count = session.query(modelo).count()
            table.add_row(nombre, f"{count:,}")

    console.print(table)

    downloads = settings.downloads_dir
    if downloads.exists():
        table2 = Table(title="Ficheros descargados")
        table2.add_column("Fichero", style="cyan")
        table2.add_column(
            "Tamaño",
            style="green",
            justify="right",
        )
        for f in sorted(downloads.iterdir()):
            if f.is_file():
                size_mb = f.stat().st_size / (1024 * 1024)
                table2.add_row(f.name, f"{size_mb:.1f} MB")
        console.print(table2)


if __name__ == "__main__":
    app()
