"""Modelos SQLAlchemy 2.0 para datos IMDb."""

from sqlalchemy import (
    Boolean,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


class Base(DeclarativeBase):
    pass


class TitleBasics(Base):
    """Titulos de IMDb (peliculas, series, cortos, etc.)."""

    __tablename__ = "title_basics"

    tconst: Mapped[str] = mapped_column(String(12), primary_key=True)
    title_type: Mapped[str | None] = mapped_column(String(20))
    primary_title: Mapped[str | None] = mapped_column(String(500))
    original_title: Mapped[str | None] = mapped_column(String(500))
    is_adult: Mapped[bool | None] = mapped_column(Boolean)
    start_year: Mapped[int | None] = mapped_column(SmallInteger)
    end_year: Mapped[int | None] = mapped_column(SmallInteger)
    runtime_minutes: Mapped[int | None] = mapped_column(Integer)
    genres: Mapped[str | None] = mapped_column(String(200))

    __table_args__ = (
        Index("ix_title_basics_type", "title_type"),
        Index("ix_title_basics_year", "start_year"),
        Index("ix_title_basics_title", "primary_title"),
    )


class TitleRatings(Base):
    """Ratings de titulos de IMDb."""

    __tablename__ = "title_ratings"

    tconst: Mapped[str] = mapped_column(String(12), primary_key=True)
    average_rating: Mapped[float | None] = mapped_column(Numeric(3, 1))
    num_votes: Mapped[int | None] = mapped_column(Integer)

    __table_args__ = (Index("ix_title_ratings_votes", "num_votes"),)


class NameBasics(Base):
    """Personas de IMDb (actores, directores, etc.)."""

    __tablename__ = "name_basics"

    nconst: Mapped[str] = mapped_column(String(12), primary_key=True)
    primary_name: Mapped[str | None] = mapped_column(String(200))
    birth_year: Mapped[int | None] = mapped_column(SmallInteger)
    death_year: Mapped[int | None] = mapped_column(SmallInteger)
    primary_profession: Mapped[str | None] = mapped_column(Text)
    known_for_titles: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (Index("ix_name_basics_name", "primary_name"),)


class TitleAkas(Base):
    """Titulos alternativos (idiomas, regiones)."""

    __tablename__ = "title_akas"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    title_id: Mapped[str | None] = mapped_column(String(12))
    ordering: Mapped[int | None] = mapped_column(SmallInteger)
    title: Mapped[str | None] = mapped_column(Text)
    region: Mapped[str | None] = mapped_column(String(10))
    language: Mapped[str | None] = mapped_column(String(10))
    types: Mapped[str | None] = mapped_column(String(100))
    attributes: Mapped[str | None] = mapped_column(String(500))
    is_original_title: Mapped[bool | None] = mapped_column(Boolean)

    __table_args__ = (
        UniqueConstraint(
            "title_id",
            "ordering",
            name="uq_title_akas_id_ord",
        ),
        Index("ix_title_akas_title_id", "title_id"),
        Index("ix_title_akas_region", "region"),
    )


class TitleCrew(Base):
    """Directores y guionistas por titulo."""

    __tablename__ = "title_crew"

    tconst: Mapped[str] = mapped_column(String(12), primary_key=True)
    directors: Mapped[str | None] = mapped_column(Text)
    writers: Mapped[str | None] = mapped_column(Text)


class TitleEpisode(Base):
    """Episodios de series."""

    __tablename__ = "title_episode"

    tconst: Mapped[str] = mapped_column(String(12), primary_key=True)
    parent_tconst: Mapped[str | None] = mapped_column(String(12))
    season_number: Mapped[int | None] = mapped_column(Integer)
    episode_number: Mapped[int | None] = mapped_column(Integer)

    __table_args__ = (
        Index("ix_title_episode_parent", "parent_tconst"),
        Index(
            "ix_title_episode_parent_season",
            "parent_tconst",
            "season_number",
            "episode_number",
        ),
    )


class TitlePrincipals(Base):
    """Cast y crew principal por titulo."""

    __tablename__ = "title_principals"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    tconst: Mapped[str | None] = mapped_column(String(12))
    ordering: Mapped[int | None] = mapped_column(SmallInteger)
    nconst: Mapped[str | None] = mapped_column(String(12))
    category: Mapped[str | None] = mapped_column(String(50))
    job: Mapped[str | None] = mapped_column(Text)
    characters: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint(
            "tconst",
            "ordering",
            name="uq_title_principals_id_ord",
        ),
        Index("ix_title_principals_tconst", "tconst"),
        Index("ix_title_principals_nconst", "nconst"),
        Index("ix_title_principals_category", "category"),
    )


# Datasets disponibles y su mapeo a tablas/ficheros
# Facilita añadir mas tablas en el futuro
DATASETS = {
    "title.basics": {
        "url": "title.basics.tsv.gz",
        "table": "title_basics",
        "model": TitleBasics,
        "columns": [
            "tconst",
            "title_type",
            "primary_title",
            "original_title",
            "is_adult",
            "start_year",
            "end_year",
            "runtime_minutes",
            "genres",
        ],
    },
    "name.basics": {
        "url": "name.basics.tsv.gz",
        "table": "name_basics",
        "model": NameBasics,
        "columns": [
            "nconst",
            "primary_name",
            "birth_year",
            "death_year",
            "primary_profession",
            "known_for_titles",
        ],
    },
    "title.akas": {
        "url": "title.akas.tsv.gz",
        "table": "title_akas",
        "model": TitleAkas,
        "columns": [
            "title_id",
            "ordering",
            "title",
            "region",
            "language",
            "types",
            "attributes",
            "is_original_title",
        ],
    },
    "title.crew": {
        "url": "title.crew.tsv.gz",
        "table": "title_crew",
        "model": TitleCrew,
        "columns": [
            "tconst",
            "directors",
            "writers",
        ],
    },
    "title.episode": {
        "url": "title.episode.tsv.gz",
        "table": "title_episode",
        "model": TitleEpisode,
        "columns": [
            "tconst",
            "parent_tconst",
            "season_number",
            "episode_number",
        ],
    },
    "title.principals": {
        "url": "title.principals.tsv.gz",
        "table": "title_principals",
        "model": TitlePrincipals,
        "columns": [
            "tconst",
            "ordering",
            "nconst",
            "category",
            "job",
            "characters",
        ],
    },
    "title.ratings": {
        "url": "title.ratings.tsv.gz",
        "table": "title_ratings",
        "model": TitleRatings,
        "columns": [
            "tconst",
            "average_rating",
            "num_votes",
        ],
    },
}

# Orden de carga
LOAD_ORDER = [
    "title.basics",
    "name.basics",
    "title.akas",
    "title.crew",
    "title.episode",
    "title.ratings",
    "title.principals",
]
