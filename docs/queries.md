# Queries de ejemplo

Coleccion de SQL utiles sobre la base de datos IMDb.

## Top 10 peliculas mejor valoradas (min 100k votos)

```sql
SELECT primary_title, start_year, average_rating, num_votes
FROM title_basics
JOIN title_ratings USING (tconst)
WHERE num_votes > 100000 AND title_type = 'movie'
ORDER BY average_rating DESC
LIMIT 10;
```

## Peores peliculas populares (min 50k votos)

```sql
SELECT primary_title, start_year, average_rating, num_votes
FROM title_basics
JOIN title_ratings USING (tconst)
WHERE num_votes > 50000 AND title_type = 'movie'
ORDER BY average_rating ASC
LIMIT 10;
```

## Rating medio por decada

```sql
SELECT
    (start_year / 10) * 10 AS decada,
    ROUND(AVG(average_rating)::numeric, 2) AS rating_medio,
    COUNT(*) AS n_peliculas
FROM title_basics
JOIN title_ratings USING (tconst)
WHERE title_type = 'movie'
  AND num_votes > 1000
  AND start_year IS NOT NULL
GROUP BY decada
ORDER BY decada;
```

## Directores mas prolificos (con al menos 10 peliculas)

```sql
SELECT
    n.primary_name,
    COUNT(*) AS n_peliculas,
    ROUND(AVG(r.average_rating)::numeric, 2) AS rating_medio
FROM title_principals p
JOIN name_basics n ON n.nconst = p.nconst
JOIN title_basics b ON b.tconst = p.tconst
JOIN title_ratings r ON r.tconst = p.tconst
WHERE p.category = 'director'
  AND b.title_type = 'movie'
  AND r.num_votes > 5000
GROUP BY n.primary_name
HAVING COUNT(*) >= 10
ORDER BY rating_medio DESC
LIMIT 20;
```

## Series con mas episodios

```sql
SELECT
    b.primary_title,
    COUNT(e.tconst) AS n_episodios
FROM title_episode e
JOIN title_basics b ON b.tconst = e.parent_tconst
GROUP BY b.primary_title
ORDER BY n_episodios DESC
LIMIT 20;
```

## Buscar por titulo (case-insensitive)

```sql
SELECT tconst, primary_title, start_year, title_type
FROM title_basics
WHERE primary_title ILIKE '%matrix%'
  AND title_type IN ('movie', 'tvSeries')
ORDER BY start_year;
```

## Peliculas en varios idiomas

```sql
SELECT
    b.primary_title,
    COUNT(DISTINCT a.language) AS n_idiomas
FROM title_basics b
JOIN title_akas a ON a.title_id = b.tconst
WHERE a.language IS NOT NULL
GROUP BY b.primary_title
ORDER BY n_idiomas DESC
LIMIT 20;
```
