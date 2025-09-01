"""
Database models for workflow persistence
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Workflow(Base):
    """Workflow model for storing workflow definitions"""
    __tablename__ = 'workflows'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(String(255), nullable=False, index=True)
    is_template = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Store the complete workflow definition as JSON
    definition = Column(JSON, nullable=False)
    
    # Versioning
    version = Column(Integer, default=1)
    parent_id = Column(String(36), ForeignKey('workflows.id'), nullable=True)
    
    # Relationships
    versions = relationship("Workflow", 
                          backref="parent", 
                          remote_side=[id],
                          cascade="all, delete-orphan")
    executions = relationship("WorkflowExecution", 
                            backref="workflow", 
                            cascade="all, delete-orphan")
    
    # Ensure unique workflow names per user
    __table_args__ = (
        UniqueConstraint('name', 'user_id', 'version', name='uix_workflow_name_user_version'),
    )
    
    def __repr__(self):
        return f"<Workflow(id='{self.id}', name='{self.name}', user_id='{self.user_id}', version={self.version})>"


class WorkflowExecution(Base):
    """WorkflowExecution model for storing execution results"""
    __tablename__ = 'workflow_executions'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(36), ForeignKey('workflows.id'), nullable=False)
    user_id = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False, default='pending')  # pending, running, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Store the execution results as JSON
    input_data = Column(JSON, nullable=True)
    results = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    
    # Metrics
    duration_ms = Column(Integer, nullable=True)
    node_count = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<WorkflowExecution(id='{self.id}', workflow_id='{self.workflow_id}', status='{self.status}')>"


class WorkflowPermission(Base):
    """WorkflowPermission model for storing user permissions on workflows"""
    __tablename__ = 'workflow_permissions'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(36), ForeignKey('workflows.id'), nullable=False)
    user_id = Column(String(255), nullable=False)
    permission = Column(String(50), nullable=False)  # read, write, execute, admin
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Ensure unique permissions per workflow and user
    __table_args__ = (
        UniqueConstraint('workflow_id', 'user_id', name='uix_workflow_permission'),
    )
    
    def __repr__(self):
        return f"<WorkflowPermission(workflow_id='{self.workflow_id}', user_id='{self.user_id}', permission='{self.permission}')>"


class WorkflowTag(Base):
    """WorkflowTag model for categorizing workflows"""
    __tablename__ = 'workflow_tags'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(36), ForeignKey('workflows.id'), nullable=False)
    tag = Column(String(100), nullable=False)
    
    # Ensure unique tags per workflow
    __table_args__ = (
        UniqueConstraint('workflow_id', 'tag', name='uix_workflow_tag'),
    )
    
    def __repr__(self):
        return f"<WorkflowTag(workflow_id='{self.workflow_id}', tag='{self.tag}')>"
