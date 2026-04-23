# IMDb - Base de datos de cine en PostgreSQL

CLI para descargar e importar los [IMDb Non-Commercial Datasets](https://developer.imdb.com/non-commercial-datasets/) a PostgreSQL local.

## Requisitos

- Python >= 3.11
- PostgreSQL en localhost

## Instalación

```bash
cd imdb
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configuración

Crear la base de datos:

```bash
createdb imdb_db
```

El fichero `.env` contiene la URL de conexión:

```
IMDB_DB_URL=postgresql+psycopg://marc@localhost:5432/imdb_db
```

## Uso

```bash
# Crear tablas
imdb init

# Descargar datasets (~500 MB)
imdb download

# Importar a PostgreSQL
imdb load

# Ver estadísticas
imdb status
```

### Opciones

```bash
# Descargar solo un dataset
imdb download --dataset title.ratings

# Re-descargar forzando
imdb download --force

# Importar vaciando tabla primero
imdb load --truncate

# Borrar y recrear tablas
imdb init --drop
```

## Esquema de datos

### title_basics (~10M filas)

Títulos de IMDb (películas, series, cortos, etc.)

| Columna | Tipo | Descripción |
|---------|------|-------------|
| tconst | VARCHAR(12) PK | Identificador IMDb (tt0000001) |
| title_type | VARCHAR(20) | movie, short, tvSeries, etc. |
| primary_title | VARCHAR(500) | Título principal |
| original_title | VARCHAR(500) | Título original |
| is_adult | BOOLEAN | Contenido adulto |
| start_year | SMALLINT | Año de estreno |
| end_year | SMALLINT | Año de fin (series) |
| runtime_minutes | INTEGER | Duración en minutos |
| genres | VARCHAR(200) | Géneros separados por coma |

### title_ratings (~1.5M filas)

Ratings de IMDb.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| tconst | VARCHAR(12) PK | Identificador IMDb |
| average_rating | NUMERIC(3,1) | Rating medio (0.0-10.0) |
| num_votes | INTEGER | Número de votos |

## Query de ejemplo

```sql
SELECT primary_title, start_year, average_rating, num_votes
FROM title_basics
JOIN title_ratings USING (tconst)
WHERE num_votes > 100000
  AND title_type = 'movie'
ORDER BY average_rating DESC
LIMIT 10;
```

## Licencia

Los datos de IMDb son para uso personal y no comercial.
Ver [IMDb Conditions of Use](https://www.imdb.com/conditions).
