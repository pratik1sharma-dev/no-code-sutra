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

# Load environment variables
load_dotenv()

# Import LangGraph services
from services.langgraph_workflows.workflow_executor import LangGraphWorkflowExecutor
from services.aiWorkflowGenerator import AIWorkflowGenerator
from services.node_registry import node_registry
from services.db import init_db, SessionLocal
from services.models import Workflow as WorkflowModel, Execution as ExecutionModel
from services.instagram_oauth import InstagramOAuthService
from services.instagram_credentials import instagram_credentials_service
from services.linkedin_oauth import LinkedInOAuthService
from services.linkedin_credentials import linkedin_credentials_service

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

app = FastAPI(
	title="No Code Sutra API",
	description="Agentic AI Workflow Platform powered by LangGraph",
	version="1.0.0"
)

# Ensure DB is initialized at startup
@app.on_event("startup")
async def _startup_init_db():
	print("🔍 Starting database initialization...")
	init_db()
	print("🔍 Database initialization complete")

# CORS middleware
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
	allow_credentials=True,
	allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
	allow_headers=["*"],
	expose_headers=["*"],
)

# Initialize services
langgraph_executor = LangGraphWorkflowExecutor()
ai_generator = AIWorkflowGenerator()
instagram_oauth_service = InstagramOAuthService()
linkedin_oauth_service = LinkedInOAuthService()

@app.get("/")
async def root():
	return {"message": "No Code Sutra - Agentic AI Workflow Platform powered by LangGraph"}

@app.get("/health")
async def health_check():
	return {"status": "healthy", "service": "No Code Sutra API", "engine": "LangGraph"}

@app.post("/api/workflows/generate", response_model=WorkflowResponse)
async def generate_workflow(request: WorkflowRequest):
	"""
	Generate an agentic workflow from natural language description
	"""
	try:
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
		print(f"Error in generate_workflow: {e}")
		raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflows/available")
async def get_available_workflows():
	"""
	Get list of available LangGraph workflows
	"""
	return {
		"workflows": [
			{
				"type": "research",
				"name": "Company Research",
				"description": "Research company information using AI",
				"nodes": ["research"],
				"input": {"company_name": "string"}
			},
			{
				"type": "lead_qualification",
				"name": "Lead Qualification",
				"description": "Complete lead qualification workflow",
				"nodes": ["research", "analyze", "score", "route"],
				"input": {"company_name": "string"}
			},
			{
				"type": "conditional_lead",
				"name": "Conditional Lead Qualification",
				"description": "Lead qualification with conditional routing",
				"nodes": ["research", "analyze", "score", "route"],
				"input": {"company_name": "string"}
			}
		]
	}

@app.get("/api/agents/available")
async def get_available_agents():
	"""
	Get list of available AI agents
	"""
	return {
		"agents": [
			{
				"name": "Research Agent",
				"description": "AI-powered company research",
				"capabilities": ["web search", "data extraction", "website scraping"],
				"input": "company_name",
				"output": "structured_company_data"
			},
			{
				"name": "Lead Analysis Agent",
				"description": "AI-powered lead analysis",
				"capabilities": ["data analysis", "lead scoring", "qualification"],
				"input": "company_data",
				"output": "lead_analysis"
			},
			{
				"name": "Lead Scoring Agent",
				"description": "AI-powered lead scoring (0-100)",
				"capabilities": ["scoring", "evaluation", "ranking"],
				"input": "company_data + analysis",
				"output": "lead_score"
			},
			{
				"name": "Lead Routing Agent",
				"description": "AI-powered lead routing decisions",
				"capabilities": ["decision_making", "routing", "classification"],
				"input": "lead_score + company_data",
				"output": "route_decision"
			}
		]
	}

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
				"node_type": "blogWriter",
				"class_name": "nodes.blog_writer.execute",
				"description": "Generates SEO-optimized blog posts"
			}
		]
	}

@app.post("/api/nodes/execute")
async def execute_node(request: NodeExecutionRequest):
	"""
	Execute a single node using LangGraph
	"""
	try:
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
async def save_workflow(req: SaveWorkflowRequest):
	try:
		db = SessionLocal()
		wf = WorkflowModel(
			id=req.id,
			name=req.name,
			description=req.description or "",
			data=req.data,
		)
		db.merge(wf)
		db.commit()
		return {"success": True}
	except Exception as e:
		return {"success": False, "error": str(e)}
	finally:
		db.close()

@app.post("/api/executions/save")
async def save_execution(result: Dict[str, Any]):
	try:
		db = SessionLocal()
		exec_model = ExecutionModel(
			id=result.get("execution_id"),
			workflow_id=result.get("workflow_id", ""),
			status=result.get("status", "completed"),
			result=result,
			nodes_executed=len(result.get("nodes_executed", [])) if isinstance(result.get("nodes_executed"), list) else int(result.get("nodes_executed", 0) or 0),
		)
		db.merge(exec_model)
		db.commit()
		return {"success": True}
	except Exception as e:
		return {"success": False, "error": str(e)}
	finally:
		db.close()


@app.get("/api/workflows")
async def list_workflows(user_id: Optional[str] = None, limit: int = 50, offset: int = 0):
	"""
	List saved workflows with optional user filtering
	"""
	try:
		db = SessionLocal()
		query = db.query(WorkflowModel)
		
		if user_id:
			# TODO: Add user_id column to WorkflowModel when user management is implemented
			# query = query.filter(WorkflowModel.user_id == user_id)
			pass
		
		workflows = query.order_by(WorkflowModel.updated_at.desc()).offset(offset).limit(limit).all()
		
		return {
			"workflows": [
				{
					"id": wf.id,
					"name": wf.name,
					"description": wf.description,
					"created_at": wf.created_at.isoformat(),
					"updated_at": wf.updated_at.isoformat(),
					"node_count": len(wf.data.get("nodes", [])),
					"status": wf.data.get("status", "draft")
				}
				for wf in workflows
			],
			"total": query.count(),
			"limit": limit,
			"offset": offset
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error listing workflows: {str(e)}")
	finally:
		db.close()


@app.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
	"""
	Get a specific workflow by ID
	"""
	try:
		db = SessionLocal()
		workflow = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
		
		if not workflow:
			raise HTTPException(status_code=404, detail="Workflow not found")
		
		return {
			"id": workflow.id,
			"name": workflow.name,
			"description": workflow.description,
			"data": workflow.data,
			"created_at": workflow.created_at.isoformat(),
			"updated_at": workflow.updated_at.isoformat()
		}
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error retrieving workflow: {str(e)}")
	finally:
		db.close()


@app.delete("/api/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
	"""
	Delete a workflow by ID
	"""
	try:
		db = SessionLocal()
		workflow = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
		
		if not workflow:
			raise HTTPException(status_code=404, detail="Workflow not found")
		
		db.delete(workflow)
		db.commit()
		
		return {"success": True, "message": "Workflow deleted successfully"}
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error deleting workflow: {str(e)}")
	finally:
		db.close()


@app.get("/api/workflows/{workflow_id}/executions")
async def get_workflow_executions(workflow_id: str, limit: int = 20, offset: int = 0):
	"""
	Get execution history for a specific workflow
	"""
	try:
		db = SessionLocal()
		executions = db.query(ExecutionModel).filter(
			ExecutionModel.workflow_id == workflow_id
		).order_by(ExecutionModel.started_at.desc()).offset(offset).limit(limit).all()
		
		return {
			"executions": [
				{
					"id": exec.id,
					"workflow_id": exec.workflow_id,
					"status": exec.status,
					"nodes_executed": exec.nodes_executed,
					"started_at": exec.started_at.isoformat(),
					"finished_at": exec.finished_at.isoformat() if exec.finished_at else None,
					"result_summary": {
						"success": exec.result.get("status") == "completed" if exec.result else False,
						"error": exec.result.get("error") if exec.result else None
					}
				}
				for exec in executions
			],
			"total": db.query(ExecutionModel).filter(ExecutionModel.workflow_id == workflow_id).count(),
			"limit": limit,
			"offset": offset
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error retrieving executions: {str(e)}")
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
async def execute_workflow(request: WorkflowExecutionRequest):
	"""
	Execute a workflow using LangGraph
	"""
	try:
		import time
		start_time = time.time()
		print(f"Executing workflow with {len(request.workflow.get('nodes', []))} nodes")
		result = langgraph_executor.execute_workflow(
			workflow_data=request.workflow,
			input_data=request.input_data
		)
		execution_time = time.time() - start_time
		if result.get('status') == 'failed':
			return {
				"success": False,
				"data": result,
				"execution_id": result.get("execution_id"),
				"status": result.get("status"),
				"error": result.get("error"),
				"execution_time": execution_time,
				"timestamp": datetime.utcnow().isoformat()
			}
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
		return response_data
	except Exception as e:
		print(f"Error in workflow execution endpoint: {e}")
		import traceback
		traceback.print_exc()
		raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

# Instagram OAuth endpoints
@app.get("/api/auth/instagram/url")
async def get_instagram_auth_url():
    """Get Instagram authorization URL for OAuth flow"""
    try:
        auth_url = instagram_oauth_service.get_authorization_url()
        return {
            "auth_url": auth_url,
            "message": "Visit this URL to authorize Instagram access"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")

@app.get("/api/auth/instagram/callback")
async def instagram_oauth_callback(code: str, state: Optional[str] = None, user_id: Optional[str] = None):
    """Handle Instagram OAuth callback and complete the flow"""
    try:
        print(f"🔍 OAuth Callback - Code: {code[:20]}..., State: {state}, User ID: {user_id}")
        
        if not code:
            print("❌ No authorization code provided")
            raise HTTPException(status_code=400, detail="Authorization code is required")
        
        # Use a default user_id if not provided (for demo purposes)
        user_id = user_id or "default_user"
        print(f"🔍 Using user_id: {user_id}")
        
        # Complete the OAuth flow
        print("🔍 Starting OAuth flow completion...")
        token_data = instagram_oauth_service.complete_oauth_flow(code)
        print(f"🔍 OAuth flow completed successfully. Token type: {token_data.get('token_type')}")
        
        # Automatically save credentials to database
        print("🔍 Attempting to save credentials to database...")
        try:
            saved = instagram_credentials_service.save_credentials(user_id, token_data)
            print(f"🔍 Credentials saved: {saved}")
        except Exception as save_error:
            print(f"❌ Error saving credentials: {save_error}")
            import traceback
            traceback.print_exc()
            # Continue even if saving fails
            saved = False
        
        # Redirect to frontend with success message
        from fastapi.responses import RedirectResponse
        
        success_url = f"http://localhost:5173/auth/instagram/callback?success=true&user_id={user_id}"
        return RedirectResponse(url=success_url, status_code=302)
    except Exception as e:
        print(f"❌ OAuth callback error: {e}")
        import traceback
        traceback.print_exc()
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


@app.get("/api/auth/instagram/credentials/{user_id}")
async def get_instagram_credentials(user_id: str):
    """Get stored Instagram credentials for a user"""
    try:
        credentials = instagram_credentials_service.get_credentials(user_id)
        
        if not credentials:
            raise HTTPException(status_code=404, detail="No credentials found for this user")
        
        # Don't return the full access token for security
        safe_credentials = {
            **credentials,
            'access_token': credentials['access_token'][:10] + '...' if credentials['access_token'] else None
        }
        
        return {
            "success": True,
            "credentials": safe_credentials
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get credentials: {str(e)}")


@app.delete("/api/auth/instagram/credentials/{user_id}")
async def delete_instagram_credentials(user_id: str):
    """Delete stored Instagram credentials for a user"""
    try:
        deleted = instagram_credentials_service.delete_credentials(user_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="No credentials found for this user")
        
        return {
            "success": True,
            "message": "Credentials deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete credentials: {str(e)}")


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


# LinkedIn OAuth endpoints
@app.get("/api/auth/linkedin/url")
async def get_linkedin_auth_url():
	"""Get LinkedIn authorization URL for OAuth flow"""
	try:
		auth_url = linkedin_oauth_service.get_authorization_url()
		return {
			"auth_url": auth_url,
			"message": "Visit this URL to authorize LinkedIn access"
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to generate LinkedIn auth URL: {str(e)}")


@app.get("/api/auth/linkedin/callback")
async def linkedin_oauth_callback(code: str, state: Optional[str] = None, user_id: Optional[str] = None):
	"""Handle LinkedIn OAuth callback and complete the flow"""
	try:
		if not code:
			raise HTTPException(status_code=400, detail="Authorization code is required")
		user_id = user_id or "default_user"
		token_data = linkedin_oauth_service.complete_oauth_flow(code)
		# Persist credentials
		saved = linkedin_credentials_service.save_credentials(user_id, token_data)
		from fastapi.responses import RedirectResponse
		success = "true" if saved else "false"
		success_url = f"http://localhost:5173/auth/linkedin/callback?success={success}&user_id={user_id}"
		return RedirectResponse(url=success_url, status_code=302)
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"LinkedIn OAuth flow failed: {str(e)}")


@app.post("/api/auth/linkedin/validate")
async def validate_linkedin_token(request: Request):
	"""Validate an existing LinkedIn access token"""
	try:
		body = await request.json()
		access_token = body.get("access_token")
		if not access_token:
			raise HTTPException(status_code=400, detail="Access token is required")
		validation = linkedin_oauth_service.validate_token(access_token)
		return validation
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"LinkedIn token validation failed: {str(e)}")


@app.get("/api/auth/linkedin/status/{user_id}")
async def get_linkedin_auth_status(user_id: str):
	"""Check if user has valid LinkedIn credentials"""
	try:
		is_valid = linkedin_credentials_service.is_token_valid(user_id)
		credentials = linkedin_credentials_service.get_credentials(user_id) if is_valid else None
		if credentials and credentials.get('access_token'):
			credentials = {
				**credentials,
				'access_token': credentials['access_token'][:10] + '...'
			}
		return {
			"authenticated": is_valid,
			"credentials": credentials if credentials else None
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to check LinkedIn auth status: {str(e)}")


@app.get("/api/auth/linkedin/credentials/{user_id}")
async def get_linkedin_credentials(user_id: str):
	"""Get stored LinkedIn credentials for a user (safe view)"""
	try:
		credentials = linkedin_credentials_service.get_credentials(user_id)
		if not credentials:
			raise HTTPException(status_code=404, detail="No LinkedIn credentials found for this user")
		if credentials.get('access_token'):
			credentials['access_token'] = credentials['access_token'][:10] + '...'
		return {"success": True, "credentials": credentials}
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to get LinkedIn credentials: {str(e)}")


@app.delete("/api/auth/linkedin/credentials/{user_id}")
async def delete_linkedin_credentials(user_id: str):
	"""Delete stored LinkedIn credentials for a user"""
	try:
		deleted = linkedin_credentials_service.delete_credentials(user_id)
		if not deleted:
			raise HTTPException(status_code=404, detail="No LinkedIn credentials found for this user")
		return {"success": True, "message": "LinkedIn credentials deleted successfully"}
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to delete LinkedIn credentials: {str(e)}")

if __name__ == "__main__":
	import uvicorn
	uvicorn.run(
		"main:app",
		host="0.0.0.0",
		port=8000,
		reload=True
	) 