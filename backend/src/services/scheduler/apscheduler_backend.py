"""
APScheduler implementation of the scheduler interface
Provides PostgreSQL-backed scheduling without Redis dependency
"""

import asyncio
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.job import Job
import pytz

# Configure module logger
logger = logging.getLogger(__name__)

from services.scheduler.base import (
    SchedulerInterface, 
    SchedulerBackend, 
    ScheduleConfig, 
    ScheduleResult, 
    ExecutionResult
)


class APSchedulerBackend(SchedulerInterface):
    """APScheduler implementation for single-server workflow scheduling"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.scheduler: Optional[AsyncIOScheduler] = None
        self._setup_scheduler()
    
    def _setup_scheduler(self):
        """Initialize APScheduler with PostgreSQL job store"""
        # Configure job store (persistent in PostgreSQL)
        jobstores = {
            'default': SQLAlchemyJobStore(
                url=self.database_url,
                tablename='apscheduler_jobs'
            )
        }
        
        # Configure executors
        executors = {
            'default': AsyncIOExecutor()
        }
        
        # Job defaults
        job_defaults = {
            'coalesce': True,  # Combine missed executions by default
            'max_instances': 1,  # Prevent concurrent executions by default
            'misfire_grace_time': 300  # 5 minutes grace period
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=pytz.UTC
        )
    
    async def start(self) -> None:
        """Start the APScheduler"""
        if self.scheduler and not self.scheduler.running:
            self.scheduler.start()
            logger.info("APScheduler started successfully")
    
    async def shutdown(self) -> None:
        """Shutdown the APScheduler"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("APScheduler shutdown completed")
    
    async def schedule_recurring_workflow(
        self,
        workflow_id: str,
        user_id: str,
        config: ScheduleConfig
    ) -> ScheduleResult:
        """Schedule a workflow for recurring execution using cron"""
        try:
            job_id = f"workflow_{workflow_id}_{user_id}_{uuid.uuid4().hex[:8]}"
            
            # Create cron trigger
            trigger = CronTrigger.from_crontab(
                config.cron_expression,
                timezone=pytz.timezone(config.timezone)
            )
            
            # Schedule the job
            job = self.scheduler.add_job(
                func=APSchedulerBackend._execute_workflow_task,
                trigger=trigger,
                args=[workflow_id, user_id, job_id],
                id=job_id,
                name=f"Workflow {workflow_id}",
                coalesce=config.coalesce,
                max_instances=config.max_instances,
                misfire_grace_time=config.misfire_grace_time,
                replace_existing=True
            )
            
            return ScheduleResult(
                job_id=job_id,
                success=True,
                message="Workflow scheduled successfully",
                next_run_time=job.next_run_time
            )
            
        except Exception as e:
            return ScheduleResult(
                job_id="",
                success=False,
                message=f"Failed to schedule workflow: {str(e)}"
            )
    
    async def schedule_one_time_workflow(
        self,
        workflow_id: str,
        user_id: str,
        run_at: datetime,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ScheduleResult:
        """Schedule a workflow for one-time execution"""
        try:
            job_id = f"onetime_{workflow_id}_{user_id}_{uuid.uuid4().hex[:8]}"
            
            # Create date trigger
            trigger = DateTrigger(run_date=run_at)
            
            # Schedule the job
            job = self.scheduler.add_job(
                func=APSchedulerBackend._execute_workflow_task,
                trigger=trigger,
                args=[workflow_id, user_id, job_id],
                id=job_id,
                name=f"One-time Workflow {workflow_id}",
                replace_existing=True
            )
            
            return ScheduleResult(
                job_id=job_id,
                success=True,
                message="One-time workflow scheduled successfully",
                next_run_time=job.next_run_time
            )
            
        except Exception as e:
            return ScheduleResult(
                job_id="",
                success=False,
                message=f"Failed to schedule one-time workflow: {str(e)}"
            )
    
    async def pause_schedule(self, job_id: str) -> bool:
        """Pause a scheduled workflow"""
        try:
            self.scheduler.pause_job(job_id)
            return True
        except Exception as e:
            logger.error(f"Failed to pause job {job_id}: {e}", exc_info=True)
            return False
    
    async def resume_schedule(self, job_id: str) -> bool:
        """Resume a paused workflow"""
        try:
            self.scheduler.resume_job(job_id)
            return True
        except Exception as e:
            logger.error(f"Failed to resume job {job_id}: {e}", exc_info=True)
            return False
    
    async def remove_schedule(self, job_id: str) -> bool:
        """Remove a scheduled workflow"""
        try:
            self.scheduler.remove_job(job_id)
            return True
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}", exc_info=True)
            return False
    
    async def get_schedule_info(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a scheduled job"""
        try:
            job: Job = self.scheduler.get_job(job_id)
            if not job:
                return None
            
            return {
                'job_id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger),
                'max_instances': job.max_instances,
                'coalesce': job.coalesce,
                'misfire_grace_time': job.misfire_grace_time
            }
        except Exception as e:
            logger.error(f"Failed to get job info for {job_id}: {e}", exc_info=True)
            return None
    
    async def list_user_schedules(self, user_id: str) -> List[Dict[str, Any]]:
        """List all schedules for a user"""
        try:
            all_jobs = self.scheduler.get_jobs()
            user_jobs = []
            
            for job in all_jobs:
                # Check if job belongs to user (job_id contains user_id)
                if f"_{user_id}_" in job.id:
                    job_info = {
                        'job_id': job.id,
                        'name': job.name,
                        'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                        'trigger': str(job.trigger),
                        'max_instances': job.max_instances,
                        'coalesce': job.coalesce
                    }
                    user_jobs.append(job_info)
            
            return user_jobs
        except Exception as e:
            logger.error(f"Failed to list user schedules for {user_id}: {e}", exc_info=True)
            return []
    
    async def get_execution_history(
        self, 
        workflow_id: str, 
        limit: int = 50
    ) -> List[ExecutionResult]:
        """Get execution history for a workflow"""
        # TODO: Implement execution history storage and retrieval
        # This would require a separate database table to store execution results
        # For now, return empty list
        return []
    
    @staticmethod
    async def _execute_workflow_task(
        workflow_id: str, 
        user_id: str, 
        job_id: str
    ) -> None:
        """Execute a scheduled workflow (called by APScheduler)"""
        execution_id = str(uuid.uuid4())
        started_at = datetime.utcnow()
        
        try:
            logger.info(f"Executing scheduled workflow", extra={
                "workflow_id": workflow_id,
                "user_id": user_id,
                "job_id": job_id,
                "execution_id": execution_id
            })
            
            # Import here to avoid circular imports
            from services.langgraph_workflows.workflow_executor import LangGraphWorkflowExecutor
            
            # Create workflow executor
            executor = LangGraphWorkflowExecutor()
            
            # Load workflow definition (you'll need to implement this)
            workflow_definition = await APSchedulerBackend._load_workflow_definition(workflow_id)
            
            if not workflow_definition:
                raise Exception(f"Workflow {workflow_id} not found")
            
            # Execute the workflow
            result = await executor.execute_workflow(
                workflow_definition,
                initial_state={'user_id': user_id, 'scheduled_execution': True}
            )
            
            completed_at = datetime.utcnow()
            
            # Log successful execution
            await APSchedulerBackend._log_execution_result(
                ExecutionResult(
                    execution_id=execution_id,
                    workflow_id=workflow_id,
                    user_id=user_id,
                    success=True,
                    started_at=started_at,
                    completed_at=completed_at,
                    result_data=result
                )
            )
            
            logger.info(f"Workflow executed successfully", extra={
                "workflow_id": workflow_id,
                "user_id": user_id,
                "execution_id": execution_id,
                "duration_ms": (completed_at - started_at).total_seconds() * 1000
            })
            
        except Exception as e:
            completed_at = datetime.utcnow()
            error_message = str(e)
            
            # Log failed execution
            await APSchedulerBackend._log_execution_result(
                ExecutionResult(
                    execution_id=execution_id,
                    workflow_id=workflow_id,
                    user_id=user_id,
                    success=False,
                    started_at=started_at,
                    completed_at=completed_at,
                    error_message=error_message
                )
            )
            
            logger.error(f"Workflow execution failed: {error_message}", extra={
                "workflow_id": workflow_id,
                "user_id": user_id,
                "execution_id": execution_id,
                "duration_ms": (completed_at - started_at).total_seconds() * 1000
            }, exc_info=True)
            
            # Re-raise to let APScheduler handle it
            raise
    
    @staticmethod
    async def _load_workflow_definition(workflow_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow definition from database"""
        # TODO: Implement workflow loading from your database
        # This is a placeholder - you'll need to integrate with your workflow storage
        return {
            'id': workflow_id,
            'nodes': [],
            'edges': []
        }
    
    @staticmethod
    async def _log_execution_result(result: ExecutionResult) -> None:
        """Log execution result to database"""
        # TODO: Implement execution logging to database
        # This would store execution results for history and monitoring
        logger.info(f"Execution logged", extra={
            "execution_id": result.execution_id,
            "workflow_id": result.workflow_id,
            "user_id": result.user_id,
            "status": "SUCCESS" if result.success else "FAILED",
            "duration_ms": (result.completed_at - result.started_at).total_seconds() * 1000 if result.completed_at and result.started_at else None
        })
    
    @property
    def backend_type(self) -> SchedulerBackend:
        """Return the scheduler backend type"""
        return SchedulerBackend.APSCHEDULER
    
    @property
    def is_distributed(self) -> bool:
        """Return whether this scheduler supports distributed execution"""
        return False

