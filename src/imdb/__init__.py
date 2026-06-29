"""CLI para datos IMDb Non-Commercial en PostgreSQL."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("imdb-db")
except PackageNotFoundError:  # paquete no instalado (ej. en tests)
    __version__ = "0.0.0"
