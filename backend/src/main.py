from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import LangGraph services
from services.langgraph_workflows.workflow_executor import LangGraphWorkflowExecutor
from services.aiWorkflowGenerator import AIWorkflowGenerator
from services.node_registry import node_registry
from services.db import init_db, save_workflow_row, save_execution_row

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
	await init_db()

@app.on_event("shutdown")
async def _shutdown_close_db():
	from services.db import close_db
	await close_db()

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
		await save_workflow_row(
			workflow_id=req.id,
			name=req.name,
			description=req.description or "",
			data=req.data,
		)
		return {"success": True}
	except Exception as e:
		return {"success": False, "error": str(e)}

@app.post("/api/executions/save")
async def save_execution(result: Dict[str, Any]):
	try:
		nodes_executed_count = (
			len(result.get("nodes_executed", []))
			if isinstance(result.get("nodes_executed"), list)
			else int(result.get("nodes_executed", 0) or 0)
		)
		await save_execution_row(
			execution_id=result.get("execution_id"),
			workflow_id=result.get("workflow_id", ""),
			status=result.get("status", "completed"),
			result=result,
			nodes_executed=nodes_executed_count,
			finished_at=result.get("finished_at"),
		)
		return {"success": True}
	except Exception as e:
		return {"success": False, "error": str(e)}

if __name__ == "__main__":
	import uvicorn
	uvicorn.run(
		"main:app",
		host="0.0.0.0",
		port=8000,
		reload=True
	) 