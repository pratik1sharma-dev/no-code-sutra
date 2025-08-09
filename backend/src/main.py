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
                "class_name": "LangGraphWorkflowNodes.ai_agent_node",
                "description": "AI-powered tasks (research, analysis, content generation)"
            },
            {
                "node_type": "data",
                "class_name": "LangGraphWorkflowNodes.data_node",
                "description": "Data processing and transformation"
            },
            {
                "node_type": "email",
                "class_name": "LangGraphWorkflowNodes.email_node",
                "description": "Email sending functionality"
            },
            {
                "node_type": "slack",
                "class_name": "LangGraphWorkflowNodes.slack_node",
                "description": "Slack messaging functionality"
            },
            {
                "node_type": "condition",
                "class_name": "LangGraphWorkflowNodes.condition_node",
                "description": "Conditional logic and routing"
            },
            {
                "node_type": "delay",
                "class_name": "LangGraphWorkflowNodes.delay_node",
                "description": "Delay and timing control"
            },
            {
                "node_type": "schedule",
                "class_name": "LangGraphWorkflowNodes.schedule_node",
                "description": "Scheduled execution"
            },
            {
                "node_type": "blogWriter",
                "class_name": "LangGraphWorkflowNodes.blog_writer_node",
                "description": "Blog content generation"
            },
            {
                "node_type": "socialMedia",
                "class_name": "LangGraphWorkflowNodes.social_media_node",
                "description": "Social media content creation"
            },
            {
                "node_type": "imageGenerator",
                "class_name": "LangGraphWorkflowNodes.image_generator_node",
                "description": "AI image generation"
            },
            {
                "node_type": "seoOptimizer",
                "class_name": "LangGraphWorkflowNodes.seo_optimizer_node",
                "description": "SEO optimization"
            }
        ],
        "total_count": 11,
        "supported_types": ["aiAgent", "data", "email", "slack", "condition", "delay", "schedule", "blogWriter", "socialMedia", "imageGenerator", "seoOptimizer"]
    }

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
        print(f"Executing workflow with {len(request.workflow.get('nodes', []))} nodes")
        
        # Execute workflow using LangGraph
        result = langgraph_executor.execute_workflow(
            workflow_data=request.workflow,
            input_data=request.input_data
        )
        
        # Ensure the result is JSON serializable
        if result.get('status') == 'failed':
            return {
                "success": False,
                "execution_id": result.get("execution_id"),
                "status": result.get("status"),
                "error": result.get("error"),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Prepare successful response
        response_data = {
            "success": True,
            "execution_id": result.get("execution_id"),
            "status": result.get("status"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add workflow results if available
        if 'node_results' in result:
            response_data['node_results'] = result['node_results']
        if 'nodes_executed' in result:
            response_data['nodes_executed'] = result['nodes_executed']
        
        # Add any other relevant data (ensure it's serializable)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 