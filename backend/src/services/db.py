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
	"""Create tables if not existing and run migrations."""
	import logging
	logger = logging.getLogger(__name__)
	
	# Import models to register them with SQLAlchemy
	from . import models  # noqa: F401
	from .scheduler.models import Base as SchedulerBase  # Import scheduler models
	
	# Create tables if they don't exist
	Base.metadata.create_all(bind=engine)
	SchedulerBase.metadata.create_all(bind=engine)
	
	# Run migrations for existing tables
	try:
		from .migrations import run_migrations
		run_migrations()
		logger.info("Database migrations completed successfully")
	except Exception as e:
		logger.error(f"Error running migrations: {e}", exc_info=True)


def get_db():
	"""FastAPI dependency to get database session"""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()