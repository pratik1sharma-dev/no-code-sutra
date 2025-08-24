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


class LinkedInCredentials(Base):
	__tablename__ = "linkedin_credentials"
	id = Column(String, primary_key=True)
	user_id = Column(String, nullable=False)
	provider = Column(String, default="linkedin")
	access_token = Column(String, nullable=False)
	refresh_token = Column(String)
	scopes = Column(String)
	expires_at = Column(DateTime)
	author_urn = Column(String)  # e.g., "urn:li:person:xxxx" or organization URN
	metadata = Column(JSONB)
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow)