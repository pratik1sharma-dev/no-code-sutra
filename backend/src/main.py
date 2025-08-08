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

# Import LangGraph workflows
from services.langgraph_workflows.ai_workflows import WorkflowFactory
from services.langgraph_workflows.workflow_executor import LangGraphWorkflowExecutor
from services.aiWorkflowGenerator import AIWorkflowGenerator
from services.workflow_executor import workflow_executor
from services.node_executors import executor_registry

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

class LangGraphExecutionRequest(BaseModel):
    workflow_type: str
    input_data: Dict[str, Any]
    user_id: Optional[str] = None

class WorkflowExecutionRequest(BaseModel):
    workflow: Dict[str, Any]
    input_data: Dict[str, Any]
    user_id: Optional[str] = None

class NodeExecutionRequest(BaseModel):
    node_type: str
    node_config: Dict[str, Any]
    input_data: Dict[str, Any]
    user_id: Optional[str] = None

class LangGraphExecutionResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    workflow_type: str
    execution_time: float
    timestamp: str

class ResearchRequest(BaseModel):
    company_name: str
    user_id: Optional[str] = None

class LeadQualificationRequest(BaseModel):
    company_name: str
    user_id: Optional[str] = None

app = FastAPI(
    title="No Code Sutra API",
    description="Agentic AI Workflow Platform powered by LangGraph",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize services lazily
workflow_factory = None
ai_generator = None
langgraph_executor = None

def get_workflow_factory():
    global workflow_factory
    if workflow_factory is None:
        from services.langgraph_workflows.ai_workflows import WorkflowFactory
        workflow_factory = WorkflowFactory()
    return workflow_factory

def get_ai_generator():
    global ai_generator
    if ai_generator is None:
        from services.aiWorkflowGenerator import AIWorkflowGenerator
        ai_generator = AIWorkflowGenerator()
    return ai_generator

def get_langgraph_executor():
    global langgraph_executor
    if langgraph_executor is None:
        from services.langgraph_workflows.workflow_executor import LangGraphWorkflowExecutor
        langgraph_executor = LangGraphWorkflowExecutor()
    return langgraph_executor

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
        
        # Use the existing AI workflow generator
        result = await get_ai_generator().generateWorkflow(request_dict)
        
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

@app.post("/api/langgraph/execute", response_model=LangGraphExecutionResponse)
async def execute_langgraph_workflow(request: LangGraphExecutionRequest):
    """
    Execute a LangGraph workflow
    """
    try:
        import time
        start_time = time.time()
        
        result = get_workflow_factory().execute_workflow(
            request.workflow_type, 
            request.input_data
        )
        
        execution_time = time.time() - start_time
        
        return LangGraphExecutionResponse(
            success=result["success"],
            data=result.get("data", {}),
            workflow_type=request.workflow_type,
            execution_time=execution_time,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/research/company")
async def research_company(request: ResearchRequest):
    """
    Research a company using LangGraph workflow
    """
    try:
        input_data = {
            "company_name": request.company_name,
            "research_data": {},
            "research_status": "pending",
            "research_error": "",
            "research_timestamp": ""
        }
        
        result = get_workflow_factory().execute_workflow("research", input_data)
        
        return {
            "success": result["success"],
            "data": result.get("data", {}),
            "workflow_type": "research",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/leads/qualify")
async def qualify_lead(request: LeadQualificationRequest):
    """
    Qualify a lead using LangGraph workflow
    """
    try:
        input_data = {
            "company_name": request.company_name,
            "research_data": {},
            "lead_analysis": "",
            "lead_score": 0,
            "route_decision": "",
            "qualification_status": "pending",
            "qualification_error": "",
            "qualification_timestamp": ""
        }
        
        result = get_workflow_factory().execute_workflow("lead_qualification", input_data)
        
        return {
            "success": result["success"],
            "data": result.get("data", {}),
            "workflow_type": "lead_qualification",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
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
    Get list of available node executors
    """
    available_types = executor_registry.list_available_types()
    executors_info = []
    
    for node_type in available_types:
        info = executor_registry.get_executor_info(node_type)
        if info:
            executors_info.append(info)
    
    return {
        "executors": executors_info,
        "total_count": len(executors_info),
        "supported_types": available_types
    }

@app.post("/api/workflows/execute")
async def execute_workflow(request: WorkflowExecutionRequest):
    """
    Execute a workflow using the new executor system
    """
    try:
        # Execute workflow using the new executor
        execution = await workflow_executor.execute_workflow(
            workflow=request.workflow,
            inputs=request.input_data
        )
        
        # Convert execution to response format
        return {
            "success": execution.status.value in ["completed"],
            "execution_id": execution.execution_id,
            "status": execution.status.value,
            "data": {
                "results": execution.results,
                "steps": [
                    {
                        "node_id": step.node_id,
                        "node_type": step.node_type,
                        "status": step.status.value,
                        "inputs": step.inputs,
                        "outputs": step.outputs,
                        "error": step.error,
                        "execution_time": step.end_time - step.start_time if step.start_time and step.end_time else None
                    }
                    for step in execution.steps
                ]
            },
            "execution_time": execution.end_time - execution.start_time if execution.start_time and execution.end_time else 0.0,
            "timestamp": datetime.utcnow().isoformat(),
            "error": execution.error
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/nodes/execute")
async def execute_node(request: NodeExecutionRequest):
    """
    Execute a single node using LangGraph
    """
    try:
        import time
        start_time = time.time()
        
        executor = get_langgraph_executor()
        result = executor.execute_node(request.node_type, request.node_config, request.input_data)
        
        execution_time = time.time() - start_time
        
        return {
            "success": result.get("status") == "completed",
            "data": result,
            "execution_time": execution_time,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 