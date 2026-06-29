"""Configuracion de IMDb usando Pydantic Settings."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Directorio raíz del proyecto (donde está pyproject.toml)
PROJECT_ROOT = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Configuracion del CLI IMDb."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        env_prefix="IMDB_",
    )

    # Base de datos PostgreSQL
    # Se puede sobreescribir con la variable de entorno
    # IMDB_DB_URL o el fichero .env
    db_url: str = "postgresql+psycopg://localhost/imdb_db"

    @property
    def data_dir(self) -> Path:
        """Directorio de datos."""
        return PROJECT_ROOT / "data"

    @property
    def downloads_dir(self) -> Path:
        """Directorio para TSV.gz descargados."""
        return self.data_dir / "downloads"

    @property
    def log_dir(self) -> Path:
        """Directorio para logs."""
        return self.data_dir / "logs"


settings = Settings()
