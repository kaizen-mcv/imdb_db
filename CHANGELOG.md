# Changelog

Todos los cambios relevantes se documentan aqui.

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el proyecto usa [SemVer](https://semver.org/lang/es/).

## [1.0.0] - 2026-04-23

### Added
- CLI `imdb` con comandos `init`, `download`, `load`, `status`.
- Descarga con reanudacion (chequeo de tamaño remoto).
- Importacion masiva via `COPY ... FROM STDIN` de PostgreSQL.
- Modelos SQLAlchemy 2.0 para los 7 datasets oficiales de IMDb.
- Configuracion via `.env` con Pydantic Settings.
- Logging centralizado con rotacion por timestamp.
- Tests unitarios de los transformadores.
- CI con GitHub Actions (Python 3.11 y 3.12).
- Licencia MIT.

[1.0.0]: https://github.com/kaizen-mcv/imdb_db/releases/tag/v1.0.0
