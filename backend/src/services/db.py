import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use Postgres only
DATABASE_URL = os.getenv(
	"DATABASE_URL",
	"postgresql+psycopg2://postgres:postgres@localhost:5432/nocodesutra",
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
	from .scheduler.models import Base as SchedulerBase  # Import scheduler models
	Base.metadata.create_all(bind=engine)
	SchedulerBase.metadata.create_all(bind=engine)


def get_db():
	"""FastAPI dependency to get database session"""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()