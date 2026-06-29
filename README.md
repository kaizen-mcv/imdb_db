# imdb-db

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PostgreSQL](https://img.shields.io/badge/postgres-13%2B-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![CI](https://github.com/kaizen-mcv/imdb_db/actions/workflows/ci.yml/badge.svg)](https://github.com/kaizen-mcv/imdb_db/actions/workflows/ci.yml)

CLI en Python para descargar los
[IMDb Non-Commercial Datasets](https://developer.imdb.com/non-commercial-datasets/)
e importarlos de forma masiva a PostgreSQL.

> Codigo bajo licencia MIT. Los datos de IMDb son solo para uso personal y no
> comercial — ver [IMDb Conditions of Use](https://www.imdb.com/conditions).

---

## Features

- **7 datasets** oficiales de IMDb (titulos, personas, episodios, ratings, ...)
- **Descarga con reanudacion**: comprueba tamaño remoto antes de re-bajar
- **Importacion masiva** con `COPY ... FROM STDIN` de PostgreSQL (rapido)
- **Streaming** desde `.tsv.gz` sin descomprimir a disco
- **Progress bars** con [Rich](https://github.com/Textualize/rich)
- **Modelos SQLAlchemy 2.0** con indices apropiados
- **CLI** con [Typer](https://typer.tiangolo.com/)

## Requisitos

- Python 3.11+
- PostgreSQL 13+ accesible (local o remoto)
- ~5 GB de espacio en disco (datos comprimidos + base de datos)

## Instalacion

```bash
git clone https://github.com/kaizen-mcv/imdb_db.git
cd imdb_db
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configuracion

```bash
createdb imdb_db
cp .env.example .env
# Editar .env con tu URL si no usas los defaults
```

Variable de entorno soportada:

| Variable      | Default                                      | Descripcion              |
| ------------- | -------------------------------------------- | ------------------------ |
| `IMDB_DB_URL` | `postgresql+psycopg://localhost/imdb_db`     | URL de conexion psycopg3 |

## Quickstart

```bash
imdb init           # crear tablas
imdb download       # bajar los 7 TSV.gz (~1.8 GB)
imdb load           # importar a PostgreSQL (~15-30 min)
imdb status         # ver filas por tabla
```

## Comandos

| Comando         | Descripcion                                        |
| --------------- | -------------------------------------------------- |
| `imdb init`     | Crear tablas. `--drop` las borra y recrea          |
| `imdb download` | Descargar TSV.gz. `--dataset X` / `--force`        |
| `imdb load`     | Importar a PostgreSQL. `--dataset X` / `--truncate`|
| `imdb status`   | Estadisticas de filas y ficheros                   |

Ejemplos:

```bash
# Descargar solo ratings
imdb download --dataset title.ratings

# Re-importar una tabla desde cero
imdb load --dataset title.basics --truncate

# Recrear el esquema entero
imdb init --drop
```

## Esquema de datos

| Tabla               | Filas aprox. | Descripcion                              |
| ------------------- | ------------ | ---------------------------------------- |
| `title_basics`      | ~11 M        | Titulos (peliculas, series, cortos, ...) |
| `title_ratings`     | ~1.5 M       | Rating medio y numero de votos           |
| `title_akas`        | ~40 M        | Titulos alternativos por region/idioma   |
| `title_crew`        | ~11 M        | Directores y guionistas (IDs)            |
| `title_episode`     | ~8 M         | Episodios de series                      |
| `title_principals`  | ~90 M        | Cast y crew principal                    |
| `name_basics`       | ~14 M        | Personas (actores, directores, ...)      |

Detalles de columnas en [`src/imdb/models.py`](src/imdb/models.py).

## Queries de ejemplo

Top 10 peliculas con mas de 100k votos:

```sql
SELECT primary_title, start_year, average_rating, num_votes
FROM title_basics
JOIN title_ratings USING (tconst)
WHERE num_votes > 100000 AND title_type = 'movie'
ORDER BY average_rating DESC
LIMIT 10;
```

Mas queries de ejemplo en [`docs/queries.md`](docs/queries.md).

## Desarrollo

```bash
pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest
```

## Licencia

Codigo: [MIT](LICENSE).

Datos de IMDb: uso personal y no comercial
([IMDb Conditions of Use](https://www.imdb.com/conditions)).
Este proyecto no redistribuye datos de IMDb — solo descarga los ficheros
publicos oficiales directamente al usuario final.
