from sqlalchemy import Column, String, DateTime, JSON, Integer
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from .db import Base, engine


def _json_type():
    try:
        return JSONB if engine.dialect.name == "postgresql" else JSON
    except Exception:
        return JSON


class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    data = Column(_json_type(), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Execution(Base):
    __tablename__ = "executions"
    id = Column(String, primary_key=True)
    workflow_id = Column(String, nullable=False)
    status = Column(String, default="running")
    result = Column(_json_type())
    nodes_executed = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)