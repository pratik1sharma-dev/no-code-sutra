from sqlalchemy import Column, String, DateTime, Integer, Index, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from .db import Base


class Workflow(Base):
	__tablename__ = "workflows"
	id = Column(String, primary_key=True)
	name = Column(String, nullable=False)
	description = Column(String, default="")
	user_id = Column(String, nullable=True, index=True)  # Added user_id field with index
	data = Column(JSONB, nullable=False)
	is_public = Column(Boolean, default=False)  # Added public flag for sharing
	version = Column(Integer, default=1)  # Added version number
	parent_id = Column(String, nullable=True)  # For tracking versions
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow)
	
	# Create indexes for common query patterns
	__table_args__ = (
		Index('idx_workflow_user_id', 'user_id'),
		Index('idx_workflow_name', 'name'),
		Index('idx_workflow_public', 'is_public'),
	)


class Execution(Base):
	__tablename__ = "executions"
	id = Column(String, primary_key=True)
	workflow_id = Column(String, nullable=False, index=True)
	user_id = Column(String, nullable=True, index=True)  # Added user_id field with index
	status = Column(String, default="running", index=True)  # Added index for status filtering
	result = Column(JSONB)
	nodes_executed = Column(Integer, default=0)
	started_at = Column(DateTime, default=datetime.utcnow, index=True)  # Added index for time-based filtering
	finished_at = Column(DateTime)
	
	# Create indexes for common query patterns
	__table_args__ = (
		Index('idx_execution_workflow_user', 'workflow_id', 'user_id'),
		Index('idx_execution_status_time', 'status', 'started_at'),
	)


class InstagramCredentials(Base):
	__tablename__ = "instagram_credentials"
	id = Column(String, primary_key=True)
	user_id = Column(String, nullable=False)
	access_token = Column(String, nullable=False)
	instagram_business_account_id = Column(String)
	page_id = Column(String)
	page_name = Column(String)
	username = Column(String)
	token_type = Column(String, default="long_lived")
	expires_at = Column(DateTime)
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow)


class CanvaCredentials(Base):
	__tablename__ = "canva_credentials"
	id = Column(String, primary_key=True)
	user_id = Column(String, nullable=False)
	access_token = Column(String, nullable=False)
	refresh_token = Column(String)
	token_type = Column(String, default="Bearer")
	scope = Column(String)
	expires_at = Column(DateTime)
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow)