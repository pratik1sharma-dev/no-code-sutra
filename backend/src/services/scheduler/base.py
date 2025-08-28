"""
Base scheduler interface for workflow scheduling
Provides abstraction layer for easy migration between scheduler backends
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class SchedulerBackend(Enum):
    """Available scheduler backends"""
    APSCHEDULER = "apscheduler"
    CELERY = "celery"


@dataclass
class ScheduleConfig:
    """Configuration for scheduling a workflow"""
    cron_expression: str
    timezone: str = "UTC"
    max_instances: int = 1
    coalesce: bool = True  # Combine missed executions
    misfire_grace_time: int = 300  # 5 minutes
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ScheduleResult:
    """Result of scheduling operation"""
    job_id: str
    success: bool
    message: str
    next_run_time: Optional[datetime] = None


@dataclass
class ExecutionResult:
    """Result of workflow execution"""
    execution_id: str
    workflow_id: str
    user_id: str
    success: bool
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None


class SchedulerInterface(ABC):
    """Abstract base class for all scheduler implementations"""
    
    @abstractmethod
    async def start(self) -> None:
        """Start the scheduler service"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the scheduler service"""
        pass
    
    @abstractmethod
    async def schedule_recurring_workflow(
        self,
        workflow_id: str,
        user_id: str,
        config: ScheduleConfig
    ) -> ScheduleResult:
        """Schedule a workflow for recurring execution"""
        pass
    
    @abstractmethod
    async def schedule_one_time_workflow(
        self,
        workflow_id: str,
        user_id: str,
        run_at: datetime,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ScheduleResult:
        """Schedule a workflow for one-time execution"""
        pass
    
    @abstractmethod
    async def pause_schedule(self, job_id: str) -> bool:
        """Pause a scheduled workflow"""
        pass
    
    @abstractmethod
    async def resume_schedule(self, job_id: str) -> bool:
        """Resume a paused workflow"""
        pass
    
    @abstractmethod
    async def remove_schedule(self, job_id: str) -> bool:
        """Remove a scheduled workflow"""
        pass
    
    @abstractmethod
    async def get_schedule_info(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a scheduled job"""
        pass
    
    @abstractmethod
    async def list_user_schedules(self, user_id: str) -> List[Dict[str, Any]]:
        """List all schedules for a user"""
        pass
    
    @abstractmethod
    async def get_execution_history(
        self, 
        workflow_id: str, 
        limit: int = 50
    ) -> List[ExecutionResult]:
        """Get execution history for a workflow"""
        pass
    
    @property
    @abstractmethod
    def backend_type(self) -> SchedulerBackend:
        """Return the scheduler backend type"""
        pass
    
    @property
    @abstractmethod
    def is_distributed(self) -> bool:
        """Return whether this scheduler supports distributed execution"""
        pass

