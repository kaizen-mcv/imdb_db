"""Conexion a base de datos PostgreSQL con SQLAlchemy."""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .config import settings

engine = create_engine(settings.db_url, echo=False)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@contextmanager
def get_session() -> Iterator[Session]:
    """Contexto de sesion que cierra siempre al salir."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """Crear todas las tablas en la base de datos."""
    from .models import Base

    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """Eliminar todas las tablas de la base de datos."""
    from .models import Base

    Base.metadata.drop_all(bind=engine)
