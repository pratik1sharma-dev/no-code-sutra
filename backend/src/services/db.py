import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use Postgres only
DATABASE_URL = os.getenv(
	"DATABASE_URL",
	"postgresql+psycopg://postgres:postgres@localhost:5432/nocodesutra",
)

# SQLAlchemy engine and session (Postgres)
engine = create_engine(
	DATABASE_URL,
	future=True,
	pool_pre_ping=True,
	echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def init_db() -> None:
	"""Create tables if not existing (no migrations)."""
	from . import models  # noqa: F401
	Base.metadata.create_all(bind=engine)