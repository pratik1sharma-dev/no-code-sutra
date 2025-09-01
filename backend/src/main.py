from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
from sqlalchemy import or_  # Added missing import

# Security imports
from middleware.auth import get_current_user, optional_auth, require_permissions, require_api_key, get_user_identifier
from middleware.rate_limiter import apply_rate_limit, rate_limiter
from middleware.security import SecurityHeadersMiddleware, InputValidationMiddleware, RequestLoggingMiddleware
from config.security import security_config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, security_config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import LangGraph services
from services.langgraph_workflows.workflow_executor import LangGraphWorkflowExecutor
from services.aiWorkflowGenerator import AIWorkflowGenerator
from services.node_registry import node_registry
from services.db import init_db, SessionLocal
from services.models import Workflow as WorkflowModel, Execution as ExecutionModel
from services.instagram_oauth import InstagramOAuthService
from services.instagram_credentials import instagram_credentials_service
from services.canva_integration import CanvaIntegration
from services.canva_credentials import canva_credentials_service
from services.scheduler.factory import SchedulerFactory

# Request/Response models
class WorkflowRequest(BaseModel):
	prompt: str
	user_id: Optional[str] = None

class WorkflowResponse(BaseModel):
	workflow: Dict[str, Any]
	suggestions: List[str] = []
	questions: List[str] = []
	metadata: Dict[str, Any] = {}
	generated_at: str

class WorkflowExecutionRequest(BaseModel):
	workflow: Dict[str, Any]
	input_data: Dict[str, Any]
	user_id: Optional[str] = None

class NodeExecutionRequest(BaseModel):
	node_type: str
	node_config: Dict[str, Any]
	input_data: Dict[str, Any]
	user_id: Optional[str] = None

class SaveWorkflowRequest(BaseModel):
	id: str
	name: str
	description: Optional[str] = ""
	data: Dict[str, Any]
	is_public: Optional[bool] = False
	version: Optional[int] = 1
	parent_id: Optional[str] = None

app = FastAPI(
	title="No Code Sutra API",
	description="Agentic AI Workflow Platform powered by LangGraph",
	version="1.0.0",
	docs_url="/docs" if not security_config.is_production() else None,
	redoc_url="/redoc" if not security_config.is_production() else None
)

# Ensure DB is initialized at startup
@app.on_event("startup")
async def _startup_init_db():
	logger.info("Starting database initialization")
	init_db()
	logger.info("Database initialization complete")
	
	# Initialize scheduler
	logger.info("Starting scheduler initialization")
	try:
		await SchedulerFactory.initialize_scheduler()
		logger.info("Scheduler initialization complete")
	except Exception as e:
		logger.error(f"Scheduler initialization failed: {e}", exc_info=True)

@app.on_event("shutdown")
async def _shutdown_scheduler():
	logger.info("Shutting down scheduler")
	try:
		await SchedulerFactory.shutdown_scheduler()
		logger.info("Scheduler shutdown complete")
	except Exception as e:
		logger.error(f"Scheduler shutdown failed: {e}", exc_info=True)

# Security middleware (order matters!)
if security_config.SECURITY_LOG_ENABLED:
	app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(InputValidationMiddleware)

# CORS middleware with secure configuration
cors_config = security_config.get_cors_config()
app.add_middleware(
	CORSMiddleware,
	**cors_config
)

# Initialize services
langgraph_executor = LangGraphWorkflowExecutor()
ai_generator = AIWorkflowGenerator()
instagram_oauth_service = InstagramOAuthService()
canva_integration = CanvaIntegration()

@app.get("/")
async def root():
	return {"message": "No Code Sutra - Agentic AI Workflow Platform powered by LangGraph"}

@app.get("/health")
async def health_check():
	return {"status": "healthy", "service": "No Code Sutra API", "engine": "LangGraph"}

@app.post("/api/workflows/generate", response_model=WorkflowResponse)
async def generate_workflow(request: WorkflowRequest, http_request: Request, user: Optional[dict] = Depends(optional_auth)):
	"""
	Generate an agentic workflow from natural language description
	"""
	try:
		# Apply rate limiting
		if security_config.RATE_LIMIT_ENABLED:
			identifier = get_user_identifier(http_request, user)
			await apply_rate_limit(http_request, identifier, "workflow", bool(user))
		# Convert WorkflowRequest to dictionary
		request_dict = {
			"prompt": request.prompt,
			"user_id": request.user_id
		}
		
		# Use the AI workflow generator
		result = await ai_generator.generateWorkflow(request_dict)
		
		return WorkflowResponse(
			workflow=result,
			suggestions=result.get("suggestions", []),
			questions=result.get("questions", []),
			metadata=result.get('metadata', {}),
			generated_at=datetime.utcnow().isoformat()
		)
	except Exception as e:
		logger.error(f"Error in generate_workflow: {e}")
		raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/executors/available")
async def get_available_executors():
	"""
	Get list of available LangGraph node types
	"""
	return {
		"executors": [
			{
				"node_type": "aiAgent",
				"class_name": "nodes.ai_agent.execute",
				"description": "AI-powered tasks (research, analysis, content generation)"
			},
			{
				"node_type": "data",
				"class_name": "nodes.data_node.execute",
				"description": "Data processing and transformation"
			},
			{
				"node_type": "email",
				"class_name": "nodes.email.execute",
				"description": "Email sending functionality"
			},
			{
				"node_type": "slack",
				"class_name": "nodes.slack.execute",
				"description": "Slack messaging functionality"
			},
			{
				"node_type": "condition",
				"class_name": "nodes.condition.execute",
				"description": "Conditional logic and routing"
			},
			{
				"node_type": "delay",
				"class_name": "nodes.delay.execute",
				"description": "Delay and timing control"
			},
			{
				"node_type": "schedule",
				"class_name": "nodes.schedule.execute",
				"description": "Scheduled execution"
			},
			{
				"node_type": "blog_writer",
				"class_name": "nodes.blog_writer.execute",
				"description": "Generates SEO-optimized blog posts"
			}
		]
	}

@app.post("/api/nodes/execute")
async def execute_node(request: NodeExecutionRequest, http_request: Request, user: Optional[dict] = Depends(optional_auth)):
	"""
	Execute a single node using LangGraph
	"""
	try:
		# Apply rate limiting
		if security_config.RATE_LIMIT_ENABLED:
			identifier = get_user_identifier(http_request, user)
			await apply_rate_limit(http_request, identifier, "workflow", bool(user))
		import time
		start_time = time.time()
		
		# Execute node using LangGraph
		result = langgraph_executor.execute_node(
			node_type=request.node_type,
			node_config=request.node_config,
			input_data=request.input_data
		)
		
		execution_time = time.time() - start_time
		
		return {
			"success": result.get("status") != "failed",
			"data": result,
			"execution_time": execution_time,
			"timestamp": datetime.utcnow().isoformat()
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflows/save")
async def save_workflow(req: SaveWorkflowRequest, http_request: Request, user: dict = Depends(get_current_user)):
	"""
	Save a workflow with versioning support
	"""
	try:
		db = SessionLocal()
		
		# Get user_id from authenticated user
		user_id = user.get('sub') if user else None
		logger.info(f"Saving workflow for user: {user_id}", extra={
			"workflow_id": req.id,
			"workflow_name": req.name,
			"user_id": user_id
		})
		
		# Check if this is an update to an existing workflow
		existing = db.query(WorkflowModel).filter(WorkflowModel.id == req.id).first()
		
		# Handle versioning
		version = req.version
		parent_id = req.parent_id
		
		if existing:
			# If updating existing workflow, increment version
			if not req.parent_id:
				parent_id = existing.id
				# Create a new ID for this version
				new_id = f"{req.id}_v{version}"
				logger.info(f"Creating new version of workflow: {new_id}", extra={
					"original_id": req.id,
					"new_id": new_id,
					"version": version
				})
				req.id = new_id
		
		# Create or update the workflow
		wf = WorkflowModel(
			id=req.id,
			name=req.name,
			description=req.description or "",
			user_id=user_id,
			data=req.data,
			is_public=req.is_public,
			version=version,
			parent_id=parent_id
		)
		db.merge(wf)
		db.commit()
		
		return {
			"success": True,
			"workflow_id": req.id,
			"version": version,
			"parent_id": parent_id
		}
	except Exception as e:
		logger.error(f"Error saving workflow: {e}", exc_info=True)
		return {"success": False, "error": str(e)}
	finally:
		db.close()

@app.post("/api/executions/save")
async def save_execution(result: Dict[str, Any]):
	try:
		db = SessionLocal()
		
		# Generate ID if not provided
		execution_id = result.get("execution_id")
		if not execution_id:
			execution_id = str(uuid.uuid4())
		
		# Extract user_id from result or use a default
		user_id = result.get("user_id", "default-user")
		
		# Log the incoming data for debugging
		print(f"Saving execution: ID={execution_id}, workflow_id={result.get('workflow_id', '')}, user_id={user_id}")
		
		exec_model = ExecutionModel(
			id=execution_id,
			workflow_id=result.get("workflow_id", ""),
			user_id=user_id,  # Add the required user_id field
			status=result.get("status", "completed"),
			result=result,
			nodes_executed=len(result.get("nodes_executed", [])) if isinstance(result.get("nodes_executed"), list) else int(result.get("nodes_executed", 0) or 0),
			started_at=datetime.fromisoformat(result.get("started_at")) if result.get("started_at") else datetime.utcnow(),
			finished_at=datetime.fromisoformat(result.get("finished_at")) if result.get("finished_at") else datetime.utcnow()
		)
		
		db.merge(exec_model)
		db.commit()
		return {"success": True}
	except Exception as e:
		print(f"Error saving execution: {str(e)}")
		return {"success": False, "error": str(e)}
	finally:
		db.close()


@app.get("/api/workflows")
async def list_workflows(
	http_request: Request, 
	user_id: Optional[str] = None, 
	limit: int = 50, 
	offset: int = 0, 
	include_public: bool = True,
	show_versions: bool = False,
	current_user: Optional[dict] = Depends(optional_auth)
):
	"""
	List saved workflows with filtering options:
	- user_id: Filter by owner
	- include_public: Include public workflows from other users
	- show_versions: Show all versions (otherwise only shows latest)
	"""
	try:
		# Apply rate limiting
		if security_config.RATE_LIMIT_ENABLED:
			identifier = get_user_identifier(http_request, current_user)
			await apply_rate_limit(http_request, identifier, "default", bool(current_user))
		
		db = SessionLocal()
		query = db.query(WorkflowModel)
		
		# Get authenticated user's ID
		auth_user_id = current_user.get('sub') if current_user else None
		
		# Filter by user_id if provided, otherwise use authenticated user
		if user_id:
			query = query.filter(WorkflowModel.user_id == user_id)
		elif auth_user_id:
			# If no specific user_id requested, show authenticated user's workflows
			query = query.filter(WorkflowModel.user_id == auth_user_id)
		
		# Include public workflows if requested
		if include_public and (user_id or auth_user_id):
			# Use union to combine user's workflows with public ones
			user_query = query
			public_query = db.query(WorkflowModel).filter(WorkflowModel.is_public == True)
			
			if user_id:
				public_query = public_query.filter(WorkflowModel.user_id != user_id)
			elif auth_user_id:
				public_query = public_query.filter(WorkflowModel.user_id != auth_user_id)
			
			# SQLAlchemy doesn't support UNION directly, so we'll fetch both and combine
			user_workflows = user_query.all()
			public_workflows = public_query.all()
			workflows = user_workflows + public_workflows
			
			# Manual sorting since we combined two queries
			workflows.sort(key=lambda wf: wf.updated_at, reverse=True)
			
			# Manual pagination
			total_count = len(workflows)
			workflows = workflows[offset:offset+limit]
			
		else:
			# If not filtering by user, apply pagination at the database level
			total_count = query.count()
			workflows = query.order_by(WorkflowModel.updated_at.desc()).offset(offset).limit(limit).all()
		
		# Filter out versions if not requested
		if not show_versions:
			# Only include workflows that don't have a parent_id (they're originals)
			workflows = [wf for wf in workflows if not wf.parent_id]
		
		return {
			"workflows": [
				{
					"id": wf.id,
					"name": wf.name,
					"description": wf.description,
					"user_id": wf.user_id,
					"is_public": wf.is_public,
					"version": wf.version,
					"parent_id": wf.parent_id,
					"created_at": wf.created_at.isoformat(),
					"updated_at": wf.updated_at.isoformat(),
					"node_count": len(wf.data.get("nodes", [])),
					"status": wf.data.get("status", "draft")
				}
				for wf in workflows
			],
			"total": total_count,
			"limit": limit,
			"offset": offset,
			"filters": {
				"user_id": user_id or auth_user_id,
				"include_public": include_public,
				"show_versions": show_versions
			}
		}
	except Exception as e:
		logger.error(f"Error listing workflows: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail=f"Error listing workflows: {str(e)}")
	finally:
		db.close()


@app.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str, http_request: Request, user: Optional[dict] = Depends(optional_auth)):
	"""
	Get a specific workflow by ID with permission checks
	"""
	try:
		db = SessionLocal()
		workflow = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
		
		if not workflow:
			raise HTTPException(status_code=404, detail="Workflow not found")
		
		# Get authenticated user's ID
		auth_user_id = user.get('sub') if user else None
		
		# Check permissions
		if workflow.user_id and workflow.user_id != auth_user_id and not workflow.is_public:
			# If workflow has an owner, current user is not the owner, and workflow is not public
			logger.warning(f"Unauthorized access attempt to workflow {workflow_id}", extra={
				"workflow_id": workflow_id,
				"requested_by": auth_user_id,
				"owner": workflow.user_id
			})
			raise HTTPException(status_code=403, detail="You don't have permission to access this workflow")
		
		# Get version history if this is the parent workflow
		versions = []
		if not workflow.parent_id:  # This is a parent workflow
			versions = db.query(WorkflowModel)\
				.filter(WorkflowModel.parent_id == workflow_id)\
				.order_by(WorkflowModel.version.desc())\
				.all()
		
		return {
			"id": workflow.id,
			"name": workflow.name,
			"description": workflow.description,
			"user_id": workflow.user_id,
			"is_public": workflow.is_public,
			"version": workflow.version,
			"parent_id": workflow.parent_id,
			"data": workflow.data,
			"created_at": workflow.created_at.isoformat(),
			"updated_at": workflow.updated_at.isoformat(),
			"versions": [
				{
					"id": v.id,
					"version": v.version,
					"updated_at": v.updated_at.isoformat()
				} for v in versions
			] if versions else []
		}
	except HTTPException:
		# Re-raise HTTP exceptions
		raise
	except Exception as e:
		logger.error(f"Error retrieving workflow: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail=f"Error retrieving workflow: {str(e)}")
	finally:
		db.close()


@app.delete("/api/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str, http_request: Request, delete_versions: bool = False, user: dict = Depends(get_current_user)):
	"""
	Delete a workflow by ID with permission checks
	- delete_versions: If true, also delete all versions of this workflow
	"""
	try:
		db = SessionLocal()
		workflow = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
		
		if not workflow:
			raise HTTPException(status_code=404, detail="Workflow not found")
		
		# Get authenticated user's ID
		auth_user_id = user.get('sub') if user else None
		
		# Check permissions - only owner can delete
		if workflow.user_id and workflow.user_id != auth_user_id:
			logger.warning(f"Unauthorized deletion attempt for workflow {workflow_id}", extra={
				"workflow_id": workflow_id,
				"requested_by": auth_user_id,
				"owner": workflow.user_id
			})
			raise HTTPException(status_code=403, detail="You don't have permission to delete this workflow")
		
		# Handle versioning
		deleted_count = 1
		deleted_versions = []
		
		# If this is a parent workflow and delete_versions is true, delete all versions
		if delete_versions and not workflow.parent_id:
			versions = db.query(WorkflowModel).filter(WorkflowModel.parent_id == workflow_id).all()
			for version in versions:
				deleted_versions.append({
					"id": version.id,
					"version": version.version
				})
				db.delete(version)
				deleted_count += 1
		
		# Delete the workflow itself
		db.delete(workflow)
		db.commit()
		
		logger.info(f"Workflow {workflow_id} deleted successfully", extra={
			"workflow_id": workflow_id,
			"deleted_by": auth_user_id,
			"deleted_versions": len(deleted_versions)
		})
		
		return {
			"success": True, 
			"message": f"Workflow deleted successfully", 
			"deleted_count": deleted_count,
			"deleted_versions": deleted_versions
		}
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error deleting workflow: {str(e)}")
	finally:
		db.close()


@app.get("/api/workflows/{workflow_id}/versions")
async def get_workflow_versions(workflow_id: str, http_request: Request, include_data: bool = False, user: Optional[dict] = Depends(optional_auth)):
	"""
	Get version history for a workflow
	- include_data: If true, include the full workflow data for each version
	"""
	try:
		db = SessionLocal()
		
		# First check if this is a valid workflow
		workflow = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
		if not workflow:
			raise HTTPException(status_code=404, detail="Workflow not found")
		
		# Get authenticated user's ID
		auth_user_id = user.get('sub') if user else None
		
		# Check permissions
		if workflow.user_id and workflow.user_id != auth_user_id and not workflow.is_public:
			logger.warning(f"Unauthorized access attempt to workflow versions {workflow_id}", extra={
				"workflow_id": workflow_id,
				"requested_by": auth_user_id,
				"owner": workflow.user_id
			})
			raise HTTPException(status_code=403, detail="You don't have permission to access this workflow")
		
		# Find the parent workflow if this is a version
		parent_id = workflow.parent_id if workflow.parent_id else workflow_id
		
		# Get all versions including the parent
		versions = db.query(WorkflowModel).filter(
			or_(
				WorkflowModel.id == parent_id,
				WorkflowModel.parent_id == parent_id
			)
		).order_by(WorkflowModel.version).all()
		
		return {
			"workflow_id": parent_id,
			"current_version": workflow.version,
			"total_versions": len(versions),
			"versions": [
				{
					"id": v.id,
					"version": v.version,
					"name": v.name,
					"description": v.description,
					"updated_at": v.updated_at.isoformat(),
					"created_at": v.created_at.isoformat(),
					"is_current": v.id == workflow_id,
					"data": v.data if include_data else None
				} for v in versions
			]
		}
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error retrieving workflow versions: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail=f"Error retrieving workflow versions: {str(e)}")
	finally:
		db.close()


@app.get("/api/workflows/{workflow_id}/executions")
async def get_workflow_executions(workflow_id: str, http_request: Request, limit: int = 20, offset: int = 0, status: Optional[str] = None, user: Optional[dict] = Depends(optional_auth)):
	"""
	Get execution history for a specific workflow with filtering options
	"""
	try:
		# Apply rate limiting
		if security_config.RATE_LIMIT_ENABLED:
			identifier = get_user_identifier(http_request, user)
			await apply_rate_limit(http_request, identifier, "workflow", bool(user))
		
		# Check if user is authenticated
		if not user:
			raise HTTPException(status_code=401, detail="Authentication required")
		
		db = SessionLocal()
		
		# Check if user has access to this workflow
		workflow = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
		if not workflow:
			raise HTTPException(status_code=404, detail="Workflow not found")
		
		# Check permissions - user must own the workflow or it must be public
		user_id = user.get('id')
		has_access = False
		
		if workflow.user_id == user_id:
			# User owns the workflow
			has_access = True
			
		elif workflow.is_public:
			# Workflow is public
			has_access = True
			
		else:
			# Check for explicit permissions
			permission = db.query(WorkflowPermission).filter(
				WorkflowPermission.workflow_id == workflow_id,
				WorkflowPermission.user_id == user_id,
				WorkflowPermission.permission.in_(['read', 'write', 'admin', 'execute'])
			).first()
			has_access = permission is not None
		
		if not has_access:
			raise HTTPException(status_code=403, detail="You don't have permission to view this workflow's executions")
		
		# Build the query with filters
		query = db.query(ExecutionModel).filter(ExecutionModel.workflow_id == workflow_id)
		
		# Add status filter if provided
		if status:
			query = query.filter(ExecutionModel.status == status)
		
		# Get total count before pagination
		total_count = query.count()
		
		# Apply sorting and pagination
		executions = query.order_by(ExecutionModel.started_at.desc()).offset(offset).limit(limit).all()
		
		return {
			"executions": [
				{
					"id": exec.id,
					"workflow_id": exec.workflow_id,
					"user_id": exec.user_id,
					"status": exec.status,
					"nodes_executed": exec.nodes_executed,
					"started_at": exec.started_at.isoformat(),
					"finished_at": exec.finished_at.isoformat() if exec.finished_at else None,
					"duration_ms": (exec.finished_at - exec.started_at).total_seconds() * 1000 if exec.finished_at else None,
					"result_summary": {
						"success": exec.result.get("status") == "completed" if exec.result else False,
						"error": exec.result.get("error") if exec.result else None
					}
				}
				for exec in executions
			],
			"total": total_count,
			"limit": limit,
			"offset": offset,
			"status_filter": status
		}
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error retrieving executions: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail=f"Error retrieving executions: {str(e)}")
	finally:
		db.close()

@app.get("/api/executions/{execution_id}")
async def get_execution_details(execution_id: str, http_request: Request, user: Optional[dict] = Depends(optional_auth)):
	"""
	Get detailed information about a specific workflow execution
	"""
	try:
		# Apply rate limiting
		if security_config.RATE_LIMIT_ENABLED:
			identifier = get_user_identifier(http_request, user)
			await apply_rate_limit(http_request, identifier, "workflow", bool(user))
		
		# Check if user is authenticated
		if not user:
			raise HTTPException(status_code=401, detail="Authentication required")
		
		db = SessionLocal()
		
		# Get the execution record
		execution = db.query(ExecutionModel).filter(ExecutionModel.id == execution_id).first()
		if not execution:
			raise HTTPException(status_code=404, detail="Execution record not found")
		
		# Get the associated workflow
		workflow = db.query(WorkflowModel).filter(WorkflowModel.id == execution.workflow_id).first()
		if not workflow:
			# Orphaned execution record, but we'll still allow access if user created the execution
			if execution.user_id != user.get('id'):
				raise HTTPException(status_code=403, detail="You don't have permission to view this execution")
		else:
			# Check permissions - user must own the workflow, own the execution, or have explicit permissions
			user_id = user.get('id')
			has_access = False
			
			if workflow.user_id == user_id or execution.user_id == user_id:
				# User owns the workflow or execution
				has_access = True
				
			elif workflow.is_public:
				# Workflow is public
				has_access = True
				
			else:
				# Check for explicit permissions
				permission = db.query(WorkflowPermission).filter(
					WorkflowPermission.workflow_id == execution.workflow_id,
					WorkflowPermission.user_id == user_id,
					WorkflowPermission.permission.in_(['read', 'write', 'admin', 'execute'])
				).first()
				has_access = permission is not None
			
			if not has_access:
				raise HTTPException(status_code=403, detail="You don't have permission to view this execution")
		
		# Calculate duration if possible
		duration_ms = None
		if execution.started_at and execution.finished_at:
			duration_ms = (execution.finished_at - execution.started_at).total_seconds() * 1000
		
		# Prepare the response
		response = {
			"id": execution.id,
			"workflow_id": execution.workflow_id,
			"user_id": execution.user_id,
			"status": execution.status,
			"nodes_executed": execution.nodes_executed,
			"started_at": execution.started_at.isoformat(),
			"finished_at": execution.finished_at.isoformat() if execution.finished_at else None,
			"duration_ms": duration_ms,
			"result": execution.result
		}
		
		return response
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error retrieving execution details: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail=f"Error retrieving execution details: {str(e)}")
	finally:
		db.close()


@app.delete("/api/executions/{execution_id}")
async def delete_execution(execution_id: str, http_request: Request, user: Optional[dict] = Depends(optional_auth)):
	"""
	Delete a specific workflow execution record
	"""
	try:
		# Apply rate limiting
		if security_config.RATE_LIMIT_ENABLED:
			identifier = get_user_identifier(http_request, user)
			await apply_rate_limit(http_request, identifier, "workflow", bool(user))
		
		# Check if user is authenticated
		if not user:
			raise HTTPException(status_code=401, detail="Authentication required")
		
		db = SessionLocal()
		
		# Get the execution record
		execution = db.query(ExecutionModel).filter(ExecutionModel.id == execution_id).first()
		if not execution:
			raise HTTPException(status_code=404, detail="Execution record not found")
		
		# Check permissions - user must own the execution or the workflow
		user_id = user.get('id')
		has_access = False
		
		if execution.user_id == user_id:
			# User owns the execution
			has_access = True
		else:
			# Check if user owns the workflow
			workflow = db.query(WorkflowModel).filter(WorkflowModel.id == execution.workflow_id).first()
			if workflow and workflow.user_id == user_id:
				has_access = True
			else:
				# Check for admin permissions
				permission = db.query(WorkflowPermission).filter(
					WorkflowPermission.workflow_id == execution.workflow_id,
					WorkflowPermission.user_id == user_id,
					WorkflowPermission.permission == 'admin'
				).first()
				has_access = permission is not None
		
		if not has_access:
			raise HTTPException(status_code=403, detail="You don't have permission to delete this execution")
		
		# Delete the execution record
		db.delete(execution)
		db.commit()
		
		return {"success": True, "message": "Execution record deleted successfully"}
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error deleting execution: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail=f"Error deleting execution: {str(e)}")
	finally:
		db.close()


@app.get("/api/nodes/registry")
async def get_node_registry():
	"""Get centralized node registry configuration"""
	try:
		# Get unique categories from the node registry
		categories = set()
		for node_type, metadata in node_registry._nodes.items():
			if metadata.is_active:
				categories.add(metadata.category.value)
		
		return {
			"success": True,
			"nodes": node_registry.get_frontend_config(),
			"count": node_registry.get_node_count(),
			"categories": list(categories)
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error getting node registry: {str(e)}")

@app.post("/api/workflows/execute")
async def execute_workflow(request: WorkflowExecutionRequest, http_request: Request, user: Optional[dict] = Depends(optional_auth)):
	"""
	Execute a workflow using LangGraph
	"""
	try:
		# Apply rate limiting
		if security_config.RATE_LIMIT_ENABLED:
			identifier = get_user_identifier(http_request, user)
			await apply_rate_limit(http_request, identifier, "workflow", bool(user))
		import time
		start_time = time.time()
		logger.info(f"Executing workflow with {len(request.workflow.get('nodes', []))} nodes", extra={
			"user_id": request.user_id,
			"node_count": len(request.workflow.get('nodes', [])),
			"workflow_id": request.workflow.get('id', 'unknown')
		})
		result = langgraph_executor.execute_workflow(
			workflow_data=request.workflow,
			input_data=request.input_data
		)
		execution_time = time.time() - start_time
		
		# Prepare response data
		if result.get('status') == 'failed':
			response_data = {
				"success": False,
				"data": result,
				"execution_id": result.get("execution_id"),
				"status": result.get("status"),
				"error": result.get("error"),
				"failed_nodes": result.get("failed_nodes", []),
				"error_details": result.get("error_details", []),
				"execution_time": execution_time,
				"timestamp": datetime.utcnow().isoformat()
			}
		else:
			response_data = {
				"success": True,
				"data": result,
				"execution_id": result.get("execution_id"),
				"status": result.get("status"),
				"execution_time": execution_time,
				"timestamp": datetime.utcnow().isoformat()
			}
			if 'node_results' in result:
				response_data['node_results'] = result['node_results']
			if 'nodes_executed' in result:
				response_data['nodes_executed'] = result['nodes_executed']
			for key, value in result.items():
				if key not in ['execution_id', 'status', 'node_results', 'nodes_executed']:
					if isinstance(value, (str, int, float, bool, type(None))):
						response_data[key] = value
					elif isinstance(value, list):
						response_data[key] = [str(item) if not isinstance(item, (str, int, float, bool, type(None))) else item for item in value]
					elif isinstance(value, dict):
						response_data[key] = {k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v for k, v in value.items()}
					else:
						response_data[key] = str(value)
		
		# Save execution result to database
		try:
			db = SessionLocal()
			user_id = request.user_id or (user.get('id') if user else None) or "anonymous"
			workflow_id = request.workflow.get('id')
			
			# Calculate nodes executed count
			nodes_executed = len(result.get("nodes_executed", [])) if isinstance(result.get("nodes_executed"), list) else 0
			
			# Create execution record
			exec_model = ExecutionModel(
				id=result.get("execution_id"),
				workflow_id=workflow_id,
				user_id=user_id,  # Add user_id to the execution record
				status=result.get("status", "completed"),
				result=result,
				nodes_executed=nodes_executed,
				started_at=datetime.fromisoformat(result.get("start_time")) if result.get("start_time") else datetime.utcnow(),
				finished_at=datetime.utcnow()
			)
			db.merge(exec_model)
			db.commit()
			logger.info(f"Saved execution result to database: {exec_model.id}")
		except Exception as e:
			logger.error(f"Error saving execution result to database: {e}", exc_info=True)
			# Don't fail the request if saving to database fails
		
		return response_data
	except Exception as e:
		logger.error(f"Error in workflow execution endpoint: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

# Instagram OAuth endpoints
@app.get("/api/auth/instagram/url")
async def get_instagram_auth_url(http_request: Request, user: Optional[dict] = Depends(optional_auth)):
	"""Get Instagram authorization URL for OAuth flow"""
	try:
		# Apply rate limiting for auth endpoints
		if security_config.RATE_LIMIT_ENABLED:
			identifier = get_user_identifier(http_request, user)
			await apply_rate_limit(http_request, identifier, "auth", bool(user))
		auth_url = instagram_oauth_service.get_authorization_url()
		return {
			"auth_url": auth_url,
			"message": "Visit this URL to authorize Instagram access"
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")

@app.get("/api/auth/instagram/callback")
async def instagram_oauth_callback(http_request: Request, code: str, state: Optional[str] = None, user_id: Optional[str] = None):
	"""Handle Instagram OAuth callback and complete the flow"""
	try:
		# Apply rate limiting for auth endpoints
		if security_config.RATE_LIMIT_ENABLED:
			identifier = get_user_identifier(http_request, None)
			await apply_rate_limit(http_request, identifier, "auth", False)
		logger.info(f"Instagram OAuth Callback received", extra={
			"state": state,
			"user_id": user_id,
			"has_code": bool(code)
		})
		
		if not code:
			logger.warning("No authorization code provided in Instagram OAuth callback")
			raise HTTPException(status_code=400, detail="Authorization code is required")
		
		# Use a default user_id if not provided (for demo purposes)
		user_id = user_id or "default_user"
		logger.info(f"Using user_id: {user_id}")
		
		# Complete the OAuth flow
		logger.info("Starting Instagram OAuth flow completion")
		token_data = instagram_oauth_service.complete_oauth_flow(code)
		logger.info(f"Instagram OAuth flow completed successfully", extra={
			"token_type": token_data.get('token_type'),
			"user_id": user_id
		})
		
		# Automatically save credentials to database
		logger.info("Attempting to save Instagram credentials to database")
		try:
			saved = instagram_credentials_service.save_credentials(user_id, token_data)
			logger.info(f"Instagram credentials saved: {saved}")
		except Exception as save_error:
			logger.error(f"Error saving Instagram credentials: {save_error}", exc_info=True)
			# Continue even if saving fails
			saved = False
		
		# Redirect to frontend with success message
		from fastapi.responses import RedirectResponse
		
		frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
		success_url = f"{frontend_url}/auth/instagram/callback?success=true&user_id={user_id}"
		return RedirectResponse(url=success_url, status_code=302)
	except Exception as e:
		logger.error(f"Instagram OAuth callback error: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail=f"OAuth flow failed: {str(e)}")

@app.post("/api/auth/instagram/validate")
async def validate_instagram_token(request: Request):
    """Validate an existing Instagram access token"""
    try:
        body = await request.json()
        access_token = body.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")
        
        validation = instagram_oauth_service.validate_token(access_token)
        
        if validation["valid"]:
            instagram_accounts = instagram_oauth_service.get_instagram_accounts(access_token)
            return {
                "valid": True,
                "user": validation["user"],
                "permissions": validation["permissions"],
                "instagram_accounts": instagram_accounts
            }
        else:
            return {
                "valid": False,
                "error": validation["error"]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token validation failed: {str(e)}")

@app.post("/api/auth/instagram/refresh")
async def refresh_instagram_token(request: Request):
    """Refresh a long-lived Instagram access token"""
    try:
        body = await request.json()
        access_token = body.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")
        
        refreshed_data = instagram_oauth_service.refresh_long_lived_token(access_token)
        
        return {
            "success": True,
            "access_token": refreshed_data["access_token"][:10] + "...",
            "expires_in": refreshed_data.get("expires_in"),
            "expires_at": (datetime.now() + timedelta(seconds=refreshed_data.get("expires_in", 5184000))).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")


@app.get("/api/auth/instagram/status/{user_id}")
async def get_instagram_auth_status(user_id: str):
    """Check if user has valid Instagram credentials"""
    try:
        is_valid = instagram_credentials_service.is_token_valid(user_id)
        credentials = instagram_credentials_service.get_credentials(user_id) if is_valid else None
        
        return {
            "authenticated": is_valid,
            "credentials": credentials if credentials else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check auth status: {str(e)}")

# Canva OAuth endpoints
@app.get("/api/auth/canva/url")
async def get_canva_auth_url():
    """Get Canva authorization URL for OAuth flow"""
    try:
        import secrets
        state = secrets.token_urlsafe(32)
        auth_url = canva_integration.get_authorization_url(state)
        
        return {
            "auth_url": auth_url,
            "state": state,
            "message": "Visit this URL to authorize Canva access"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Canva auth URL: {str(e)}")

@app.get("/api/auth/canva/callback")
async def canva_oauth_callback(code: str = None, state: Optional[str] = None, user_id: Optional[str] = None, error: Optional[str] = None, error_description: Optional[str] = None):
    """Handle Canva OAuth callback and complete the flow"""
    try:
        logger.info("Canva OAuth Callback Received", extra={
            "has_code": bool(code),
            "state": state,
            "user_id": user_id,
            "error": error,
            "error_description": error_description
        })
        
        if error:
            logger.error(f"Canva OAuth Error: {error} - {error_description}")
            raise HTTPException(status_code=400, detail=f"Canva OAuth error: {error} - {error_description}")
        
        if not code:
            logger.warning("No authorization code provided in Canva OAuth callback")
            raise HTTPException(status_code=400, detail="Authorization code is required")
        
        # Use a default user_id if not provided
        user_id = user_id or "default_user"
        
        logger.info("Starting Canva OAuth flow completion", extra={"user_id": user_id})
        token_data = canva_integration.exchange_code_for_token(code, state)
        logger.info("Canva OAuth flow completed successfully")
        
        # Save credentials to database
        try:
            saved = canva_credentials_service.save_credentials(user_id, token_data)
            logger.info(f"Canva credentials saved: {saved}", extra={"user_id": user_id})
        except Exception as save_error:
            logger.error(f"Error saving Canva credentials: {save_error}", exc_info=True)
            saved = False
        
        # Redirect to frontend with success message
        from fastapi.responses import RedirectResponse
        
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        success_url = f"{frontend_url}/auth/canva/callback?canva_success=true&user_id={user_id}"
        return RedirectResponse(url=success_url, status_code=302)
        
    except Exception as e:
        logger.error(f"Canva OAuth callback error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Canva OAuth flow failed: {str(e)}")

@app.post("/api/auth/canva/reconnect")
async def reconnect_canva(request: Request):
    """Reconnect to Canva - clear old credentials and generate new auth URL"""
    try:
        import secrets
        
        # Get user ID from request body or use default
        body = await request.json()
        user_id = body.get("user_id", "default_user")
        
        # Clear old credentials
        canva_credentials_service.delete_credentials(user_id)
        
        # Generate new authorization URL with updated scopes
        state = secrets.token_urlsafe(32)
        auth_url = canva_integration.get_authorization_url(state)
        
        return {
            "success": True,
            "message": "Old credentials cleared. Please re-authenticate with Canva.",
            "auth_url": auth_url,
            "state": state,
            "requires_reauth": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Canva reconnect failed: {str(e)}")

@app.post("/api/auth/canva/refresh")
async def refresh_canva_token(request: Request):
    """Refresh a Canva access token (legacy endpoint - now redirects to reconnect)"""
    try:
        # Get user ID from request body or use default
        body = await request.json()
        user_id = body.get("user_id", "default_user")
        
        # For JWT tokens, we need to re-authenticate since there's no refresh token
        # This is a limitation of Canva's JWT-based OAuth flow
        return {
            "success": False,
            "message": "JWT tokens cannot be refreshed. Please use /api/auth/canva/reconnect to re-authenticate.",
            "requires_reauth": True,
            "reconnect_endpoint": "/api/auth/canva/reconnect"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Canva token refresh failed: {str(e)}")

@app.get("/api/auth/canva/status/{user_id}")
async def get_canva_auth_status(user_id: str):
    """Check if Canva is authenticated for a user"""
    try:
        is_valid = canva_credentials_service.is_token_valid(user_id)
        credentials = canva_credentials_service.get_credentials(user_id) if is_valid else None
        
        return {
            "authenticated": is_valid,
            "credentials": credentials if credentials else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check Canva auth status: {str(e)}")

# Canva Template and Design endpoints
@app.get("/api/canva/templates")
async def get_canva_templates(query: Optional[str] = None, category: Optional[str] = None, limit: int = 20, user_id: str = "default_user"):
    """Get Canva templates"""
    try:
        # Get credentials from database
        credentials = canva_credentials_service.get_credentials(user_id)
        if not credentials:
            raise HTTPException(status_code=401, detail="No valid Canva credentials found. Please authenticate first.")
        
        # Initialize Canva integration with stored tokens
        canva_integration.access_token = credentials.get('access_token')
        
        templates = canva_integration.search_templates(query=query, category=category, limit=limit)
        
        return {
            "success": True,
            "templates": templates,
            "count": len(templates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Canva templates: {str(e)}")

@app.get("/api/canva/templates/{template_id}")
async def get_canva_template_details(template_id: str, user_id: str = "default_user"):
    """Get detailed information about a specific Canva template"""
    try:
        # Get credentials from database
        credentials = canva_credentials_service.get_credentials(user_id)
        if not credentials:
            raise HTTPException(status_code=401, detail="No valid Canva credentials found. Please authenticate first.")
        
        # Initialize Canva integration with stored tokens
        canva_integration.access_token = credentials.get('access_token')
        
        template_details = canva_integration.get_template_details(template_id)
        
        return {
            "success": True,
            "template": template_details
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get template details: {str(e)}")

@app.post("/api/canva/templates/{template_id}/create-design")
async def create_canva_design(template_id: str, request: Request, user_id: str = "default_user"):
    """Create a design from a template with custom content"""
    try:
        # Get credentials from database
        credentials = canva_credentials_service.get_credentials(user_id)
        if not credentials:
            raise HTTPException(status_code=401, detail="No valid Canva credentials found. Please authenticate first.")
        
        # Initialize Canva integration with stored tokens
        canva_integration.access_token = credentials.get('access_token')
        
        # Get content from request body
        body = await request.json()
        content_data = body.get('content', {})
        
        # Create design (will use fallback in dev mode)
        design = canva_integration.apply_content_to_template(template_id, content_data)
        
        return {
            "success": True,
            "design": design,
            "method": design.get('method', 'unknown')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create design: {str(e)}")

@app.get("/api/canva/templates/{template_id}/download")
async def download_canva_template(template_id: str, format: str = "png", user_id: str = "default_user"):
    """Download a Canva template as an image"""
    try:
        # Get credentials from database
        credentials = canva_credentials_service.get_credentials(user_id)
        if not credentials:
            raise HTTPException(status_code=401, detail="No valid Canva credentials found. Please authenticate first.")
        
        # Initialize Canva integration with stored tokens
        canva_integration.access_token = credentials.get('access_token')
        
        # Download template
        template_image = canva_integration.download_template(template_id, format)
        
        from fastapi.responses import Response
        return Response(
            content=template_image,
            media_type=f"image/{format}",
            headers={"Content-Disposition": f"attachment; filename=template_{template_id}.{format}"}
        )
    except Exception as e:
        		raise HTTPException(status_code=500, detail=f"Failed to download template: {str(e)}")

@app.get("/api/workflows/stream")
async def stream_workflow(workflow_json: str, input_json: str, http_request: Request, user: Optional[dict] = Depends(optional_auth)):
	"""Stream workflow execution events via Server-Sent Events (SSE).
	- Accepts URL-encoded JSON strings for workflow and input
	- Returns text/event-stream with data: <json> lines
	"""
	try:
		# Apply rate limiting
		if security_config.RATE_LIMIT_ENABLED:
			identifier = get_user_identifier(http_request, user)
			await apply_rate_limit(http_request, identifier, "workflow", bool(user))
		import json as _json
		workflow = _json.loads(workflow_json)
		inputs = _json.loads(input_json)
		stream = langgraph_executor.stream_execution(workflow, inputs)
		return StreamingResponse(stream, media_type="text/event-stream")
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")

# Include additional routes
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from api.scheduler_routes import router as scheduler_router
from api.auth_routes import router as auth_router
app.include_router(scheduler_router)
app.include_router(auth_router)

if __name__ == "__main__":
	import uvicorn
	port = int(os.getenv("PORT", 8000))
	uvicorn.run(
		"main:app",
		host="0.0.0.0",
		port=port,
		reload=False
	) 