from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from .db import Base


class Workflow(Base):
	__tablename__ = "workflows"
	id = Column(String, primary_key=True)
	name = Column(String, nullable=False)
	description = Column(String, default="")
	data = Column(JSONB, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow)


class Execution(Base):
	__tablename__ = "executions"
	id = Column(String, primary_key=True)
	workflow_id = Column(String, nullable=False)
	status = Column(String, default="running")
	result = Column(JSONB)
	nodes_executed = Column(Integer, default=0)
	started_at = Column(DateTime, default=datetime.utcnow)
	finished_at = Column(DateTime)