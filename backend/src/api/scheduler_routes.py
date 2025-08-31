"""
FastAPI routes for workflow scheduling
Provides REST API endpoints for managing workflow schedules
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from services.scheduler.service import WorkflowSchedulerService
from services.db import get_db


# Pydantic models for API
class CreateRecurringScheduleRequest(BaseModel):
    workflow_id: str = Field(..., description="UUID of the workflow to schedule")
    name: str = Field(..., description="Human-readable name for the schedule")
    cron_expression: str = Field(..., description="Cron expression for scheduling (e.g., '0 9 * * MON')")
    timezone: str = Field(default="UTC", description="Timezone for the schedule")
    description: Optional[str] = Field(None, description="Optional description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class CreateOneTimeScheduleRequest(BaseModel):
    workflow_id: str = Field(..., description="UUID of the workflow to schedule")
    name: str = Field(..., description="Human-readable name for the schedule")
    run_at: datetime = Field(..., description="When to run the workflow (ISO format)")
    description: Optional[str] = Field(None, description="Optional description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ScheduleResponse(BaseModel):
    success: bool
    schedule_id: Optional[str] = None
    backend_job_id: Optional[str] = None
    message: str
    next_run_time: Optional[str] = None
    run_at: Optional[str] = None


class ScheduleListItem(BaseModel):
    schedule_id: str
    workflow_id: str
    name: str
    description: Optional[str]
    cron_expression: str
    timezone: str
    is_active: bool
    backend_type: str
    created_at: str
    last_execution_at: Optional[str]
    next_execution_at: Optional[str]
    execution_count: int
    metadata: Optional[Dict[str, Any]]


class ExecutionHistoryItem(BaseModel):
    execution_id: str
    workflow_id: str
    execution_type: str
    status: str
    success: Optional[bool]
    started_at: str
    completed_at: Optional[str]
    duration_seconds: Optional[int]
    error_message: Optional[str]
    node_results_count: int


class SchedulerStatusResponse(BaseModel):
    backend: str
    is_distributed: bool
    active_schedules: int
    executions_24h: int
    success_rate_24h: float
    status: str
    error: Optional[str] = None


# Create router
router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


def get_scheduler_service(db: Session = Depends(get_db)) -> WorkflowSchedulerService:
    """Dependency to get scheduler service"""
    return WorkflowSchedulerService(db)


@router.options("/recurring")
async def recurring_options():
    """Handle OPTIONS preflight request for recurring endpoint"""
    return {"message": "OK"}

@router.post("/recurring", response_model=ScheduleResponse)
async def create_recurring_schedule(
    request: CreateRecurringScheduleRequest,
    scheduler_service: WorkflowSchedulerService = Depends(get_scheduler_service),
    user_id: str = "default_user"  # TODO: Get from JWT token/auth
):
    """Create a recurring workflow schedule"""
    try:
        result = await scheduler_service.create_recurring_schedule(
            workflow_id=request.workflow_id,
            user_id=user_id,
            name=request.name,
            cron_expression=request.cron_expression,
            timezone=request.timezone,
            description=request.description,
            metadata=request.metadata
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return ScheduleResponse(
            success=True,
            schedule_id=result["schedule_id"],
            backend_job_id=result["backend_job_id"],
            message=result["message"],
            next_run_time=result["next_run_time"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create recurring schedule: {str(e)}"
        )


@router.post("/one-time", response_model=ScheduleResponse)
async def create_one_time_schedule(
    request: CreateOneTimeScheduleRequest,
    scheduler_service: WorkflowSchedulerService = Depends(get_scheduler_service),
    user_id: str = "default_user"  # TODO: Get from JWT token/auth
):
    """Create a one-time workflow schedule"""
    try:
        result = await scheduler_service.create_one_time_schedule(
            workflow_id=request.workflow_id,
            user_id=user_id,
            name=request.name,
            run_at=request.run_at,
            description=request.description,
            metadata=request.metadata
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return ScheduleResponse(
            success=True,
            schedule_id=result["schedule_id"],
            backend_job_id=result["backend_job_id"],
            message=result["message"],
            run_at=result["run_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create one-time schedule: {str(e)}"
        )


@router.post("/{schedule_id}/pause")
async def pause_schedule(
    schedule_id: str,
    scheduler_service: WorkflowSchedulerService = Depends(get_scheduler_service),
    user_id: str = "default_user"  # TODO: Get from JWT token/auth
):
    """Pause a workflow schedule"""
    try:
        result = await scheduler_service.pause_schedule(schedule_id, user_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {"success": True, "message": result["message"]}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause schedule: {str(e)}"
        )


@router.post("/{schedule_id}/resume")
async def resume_schedule(
    schedule_id: str,
    scheduler_service: WorkflowSchedulerService = Depends(get_scheduler_service),
    user_id: str = "default_user"  # TODO: Get from JWT token/auth
):
    """Resume a paused workflow schedule"""
    try:
        result = await scheduler_service.resume_schedule(schedule_id, user_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {"success": True, "message": result["message"]}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume schedule: {str(e)}"
        )


@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: str,
    scheduler_service: WorkflowSchedulerService = Depends(get_scheduler_service),
    user_id: str = "default_user"  # TODO: Get from JWT token/auth
):
    """Delete a workflow schedule"""
    try:
        result = await scheduler_service.delete_schedule(schedule_id, user_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "success": True, 
            "message": result["message"],
            "backend_removal_success": result.get("backend_removal_success", True)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete schedule: {str(e)}"
        )


@router.get("/", response_model=List[ScheduleListItem])
async def list_user_schedules(
    scheduler_service: WorkflowSchedulerService = Depends(get_scheduler_service),
    user_id: str = "default_user"  # TODO: Get from JWT token/auth
):
    """List all schedules for a user"""
    try:
        schedules = scheduler_service.list_user_schedules(user_id)
        return [ScheduleListItem(**schedule) for schedule in schedules]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list schedules: {str(e)}"
        )


@router.get("/{workflow_id}/history", response_model=List[ExecutionHistoryItem])
async def get_execution_history(
    workflow_id: str,
    scheduler_service: WorkflowSchedulerService = Depends(get_scheduler_service),
    limit: int = 50,
    user_id: str = "default_user"  # TODO: Get from JWT token/auth
):
    """Get execution history for a workflow"""
    try:
        history = scheduler_service.get_execution_history(workflow_id, user_id, limit)
        return [ExecutionHistoryItem(**item) for item in history]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution history: {str(e)}"
        )


@router.get("/status", response_model=SchedulerStatusResponse)
async def get_scheduler_status(
    scheduler_service: WorkflowSchedulerService = Depends(get_scheduler_service)
):
    """Get current scheduler status and metrics"""
    try:
        status = await scheduler_service.get_scheduler_status()
        return SchedulerStatusResponse(**status)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get scheduler status: {str(e)}"
        )


# Health check endpoint
@router.get("/health")
async def scheduler_health_check():
    """Simple health check for scheduler service"""
    try:
        from ..services.scheduler.factory import SchedulerFactory
        backend_info = SchedulerFactory.get_backend_info()
        
        return {
            "status": "healthy",
            "backend": backend_info["backend"],
            "is_distributed": backend_info.get("is_distributed", False),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

