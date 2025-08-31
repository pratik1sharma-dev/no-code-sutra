"""
High-level scheduler service for workflow scheduling
Provides business logic layer on top of scheduler backends
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import uuid
import logging

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

# Configure module logger
logger = logging.getLogger(__name__)

from services.scheduler.base import ScheduleConfig, ScheduleResult, ExecutionResult
from services.scheduler.factory import get_scheduler
from services.scheduler.models import WorkflowSchedule, WorkflowExecution


class WorkflowSchedulerService:
    """High-level service for managing workflow schedules"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.scheduler = get_scheduler()
    
    async def create_recurring_schedule(
        self,
        workflow_id: str,
        user_id: str,
        name: str,
        cron_expression: str,
        timezone: str = "UTC",
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new recurring workflow schedule"""
        
        # Validate cron expression
        if not self._validate_cron_expression(cron_expression):
            return {
                "success": False,
                "error": "Invalid cron expression",
                "schedule_id": None
            }
        
        try:
            # Create schedule config
            config = ScheduleConfig(
                cron_expression=cron_expression,
                timezone=timezone,
                user_metadata=metadata
            )
            
            # Schedule with backend
            result = await self.scheduler.schedule_recurring_workflow(
                workflow_id=workflow_id,
                user_id=user_id,
                config=config
            )
            
            if not result.success:
                return {
                    "success": False,
                    "error": result.message,
                    "schedule_id": None
                }
            
            # Save to database
            schedule = WorkflowSchedule(
                workflow_id=uuid.UUID(workflow_id),
                user_id=uuid.UUID(user_id),
                name=name,
                description=description,
                cron_expression=cron_expression,
                timezone=timezone,
                backend_type=self.scheduler.backend_type.value,
                backend_job_id=result.job_id,
                next_execution_at=result.next_run_time,
                user_metadata=metadata
            )
            
            self.db.add(schedule)
            self.db.commit()
            
            return {
                "success": True,
                "schedule_id": str(schedule.id),
                "backend_job_id": result.job_id,
                "next_run_time": result.next_run_time.isoformat() if result.next_run_time else None,
                "message": "Schedule created successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "error": f"Failed to create schedule: {str(e)}",
                "schedule_id": None
            }
    
    async def create_one_time_schedule(
        self,
        workflow_id: str,
        user_id: str,
        name: str,
        run_at: datetime,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a one-time workflow schedule"""
        
        # Validate run time is in the future
        if run_at <= datetime.utcnow():
            return {
                "success": False,
                "error": "Schedule time must be in the future",
                "schedule_id": None
            }
        
        try:
            # Schedule with backend
            result = await self.scheduler.schedule_one_time_workflow(
                workflow_id=workflow_id,
                user_id=user_id,
                run_at=run_at,
                user_metadata=metadata
            )
            
            if not result.success:
                return {
                    "success": False,
                    "error": result.message,
                    "schedule_id": None
                }
            
            # Save to database
            schedule = WorkflowSchedule(
                workflow_id=uuid.UUID(workflow_id),
                user_id=uuid.UUID(user_id),
                name=name,
                description=description,
                cron_expression="",  # One-time schedules don't have cron
                timezone="UTC",
                backend_type=self.scheduler.backend_type.value,
                backend_job_id=result.job_id,
                next_execution_at=run_at,
                user_metadata=metadata
            )
            
            self.db.add(schedule)
            self.db.commit()
            
            return {
                "success": True,
                "schedule_id": str(schedule.id),
                "backend_job_id": result.job_id,
                "run_at": run_at.isoformat(),
                "message": "One-time schedule created successfully"
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "error": f"Failed to create one-time schedule: {str(e)}",
                "schedule_id": None
            }
    
    async def pause_schedule(self, schedule_id: str, user_id: str) -> Dict[str, Any]:
        """Pause a workflow schedule"""
        try:
            # Get schedule from database
            schedule = self.db.query(WorkflowSchedule).filter(
                and_(
                    WorkflowSchedule.id == uuid.UUID(schedule_id),
                    WorkflowSchedule.user_id == uuid.UUID(user_id),
                    WorkflowSchedule.is_active == True
                )
            ).first()
            
            if not schedule:
                return {
                    "success": False,
                    "error": "Schedule not found or already inactive"
                }
            
            # Pause in backend
            success = await self.scheduler.pause_schedule(schedule.backend_job_id)
            
            if success:
                schedule.is_active = False
                self.db.commit()
                
                return {
                    "success": True,
                    "message": "Schedule paused successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to pause schedule in backend"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to pause schedule: {str(e)}"
            }
    
    async def resume_schedule(self, schedule_id: str, user_id: str) -> Dict[str, Any]:
        """Resume a paused workflow schedule"""
        try:
            # Get schedule from database
            schedule = self.db.query(WorkflowSchedule).filter(
                and_(
                    WorkflowSchedule.id == uuid.UUID(schedule_id),
                    WorkflowSchedule.user_id == uuid.UUID(user_id),
                    WorkflowSchedule.is_active == False
                )
            ).first()
            
            if not schedule:
                return {
                    "success": False,
                    "error": "Schedule not found or already active"
                }
            
            # Resume in backend
            success = await self.scheduler.resume_schedule(schedule.backend_job_id)
            
            if success:
                schedule.is_active = True
                self.db.commit()
                
                return {
                    "success": True,
                    "message": "Schedule resumed successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to resume schedule in backend"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to resume schedule: {str(e)}"
            }
    
    async def delete_schedule(self, schedule_id: str, user_id: str) -> Dict[str, Any]:
        """Delete a workflow schedule"""
        try:
            # Get schedule from database
            schedule = self.db.query(WorkflowSchedule).filter(
                and_(
                    WorkflowSchedule.id == uuid.UUID(schedule_id),
                    WorkflowSchedule.user_id == uuid.UUID(user_id)
                )
            ).first()
            
            if not schedule:
                return {
                    "success": False,
                    "error": "Schedule not found"
                }
            
            # Remove from backend
            success = await self.scheduler.remove_schedule(schedule.backend_job_id)
            
            # Delete from database (even if backend removal failed)
            self.db.delete(schedule)
            self.db.commit()
            
            return {
                "success": True,
                "message": "Schedule deleted successfully",
                "backend_removal_success": success
            }
                
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "error": f"Failed to delete schedule: {str(e)}"
            }
    
    def list_user_schedules(self, user_id: str) -> List[Dict[str, Any]]:
        """List all schedules for a user"""
        try:
            schedules = self.db.query(WorkflowSchedule).filter(
                WorkflowSchedule.user_id == uuid.UUID(user_id)
            ).order_by(desc(WorkflowSchedule.created_at)).all()
            
            result = []
            for schedule in schedules:
                result.append({
                    "schedule_id": str(schedule.id),
                    "workflow_id": str(schedule.workflow_id),
                    "name": schedule.name,
                    "description": schedule.description,
                    "cron_expression": schedule.cron_expression,
                    "timezone": schedule.timezone,
                    "is_active": schedule.is_active,
                    "backend_type": schedule.backend_type,
                    "created_at": schedule.created_at.isoformat(),
                    "last_execution_at": schedule.last_execution_at.isoformat() if schedule.last_execution_at else None,
                    "next_execution_at": schedule.next_execution_at.isoformat() if schedule.next_execution_at else None,
                    "execution_count": schedule.execution_count,
                    "metadata": schedule.user_metadata
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to list user schedules: {e}", extra={"user_id": user_id}, exc_info=True)
            return []
    
    def get_execution_history(
        self, 
        workflow_id: str, 
        user_id: str, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get execution history for a workflow"""
        try:
            executions = self.db.query(WorkflowExecution).filter(
                and_(
                    WorkflowExecution.workflow_id == uuid.UUID(workflow_id),
                    WorkflowExecution.user_id == uuid.UUID(user_id)
                )
            ).order_by(desc(WorkflowExecution.started_at)).limit(limit).all()
            
            result = []
            for execution in executions:
                result.append({
                    "execution_id": str(execution.id),
                    "workflow_id": str(execution.workflow_id),
                    "execution_type": execution.execution_type,
                    "status": execution.status,
                    "success": execution.success,
                    "started_at": execution.started_at.isoformat(),
                    "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                    "duration_seconds": execution.duration_seconds,
                    "error_message": execution.error_message,
                    "node_results_count": execution.node_results_count
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get execution history: {e}", extra={"workflow_id": workflow_id}, exc_info=True)
            return []
    
    def _validate_cron_expression(self, cron_expression: str) -> bool:
        """Validate cron expression format"""
        try:
            from croniter import croniter
            return croniter.is_valid(cron_expression)
        except ImportError:
            # Fallback basic validation if croniter not available
            parts = cron_expression.split()
            return len(parts) == 5
        except Exception:
            return False
    
    async def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status and metrics"""
        try:
            # Get backend info
            backend_info = self.scheduler.backend_type.value
            is_distributed = self.scheduler.is_distributed
            
            # Get active schedules count
            active_schedules = self.db.query(WorkflowSchedule).filter(
                WorkflowSchedule.is_active == True
            ).count()
            
            # Get recent execution stats
            recent_executions = self.db.query(WorkflowExecution).filter(
                WorkflowExecution.started_at >= datetime.utcnow() - timedelta(hours=24)
            ).all()
            
            success_count = sum(1 for e in recent_executions if e.success)
            total_executions = len(recent_executions)
            success_rate = (success_count / total_executions * 100) if total_executions > 0 else 0
            
            return {
                "backend": backend_info,
                "is_distributed": is_distributed,
                "active_schedules": active_schedules,
                "executions_24h": total_executions,
                "success_rate_24h": round(success_rate, 2),
                "status": "healthy"
            }
            
        except Exception as e:
            return {
                "backend": "unknown",
                "is_distributed": False,
                "status": "error",
                "error": str(e)
            }

