"""
Database models for workflow scheduling
Works with both APScheduler and Celery backends
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class WorkflowSchedule(Base):
    """User-facing workflow schedule tracking"""
    __tablename__ = 'workflow_schedules'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Schedule configuration
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    cron_expression = Column(String(100), nullable=False)
    timezone = Column(String(50), default='UTC')
    
    # Backend-specific job tracking
    backend_type = Column(String(50), nullable=False)  # 'apscheduler' or 'celery'
    backend_job_id = Column(String(255), nullable=False)  # APScheduler job_id or Celery task_id
    
    # Status and metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_execution_at = Column(DateTime(timezone=True), nullable=True)
    next_execution_at = Column(DateTime(timezone=True), nullable=True)
    execution_count = Column(Integer, default=0)
    
    # Additional configuration
    config = Column(JSON, nullable=True)  # Store additional scheduler config
    user_metadata = Column(JSON, nullable=True)  # Store user metadata


class WorkflowExecution(Base):
    """Workflow execution history and results"""
    __tablename__ = 'workflow_executions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schedule_id = Column(UUID(as_uuid=True), nullable=True)  # Link to WorkflowSchedule
    workflow_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Execution details
    execution_type = Column(String(50), nullable=False)  # 'scheduled', 'manual', 'one_time'
    status = Column(String(50), nullable=False)  # 'running', 'completed', 'failed', 'cancelled'
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Results
    success = Column(Boolean, nullable=True)
    error_message = Column(Text, nullable=True)
    result_data = Column(JSON, nullable=True)  # Store execution results
    
    # Metadata
    backend_execution_id = Column(String(255), nullable=True)  # Backend-specific execution ID
    node_results_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SchedulerHealth(Base):
    """Scheduler health and monitoring"""
    __tablename__ = 'scheduler_health'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    backend_type = Column(String(50), nullable=False)
    
    # Health metrics
    is_running = Column(Boolean, default=False)
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    active_jobs_count = Column(Integer, default=0)
    failed_jobs_count = Column(Integer, default=0)
    
    # Performance metrics
    avg_execution_time_seconds = Column(Integer, nullable=True)
    success_rate_percentage = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# Migration script for creating tables
def create_scheduler_tables(engine):
    """Create scheduler-related tables"""
    Base.metadata.create_all(engine)
    print("✅ Scheduler tables created successfully")

