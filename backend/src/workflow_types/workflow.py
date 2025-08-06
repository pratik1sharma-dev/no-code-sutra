from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

# LangGraph State Types
class ResearchState(TypedDict):
    company_name: str
    research_data: Dict[str, Any]
    research_status: str
    research_error: str
    research_timestamp: str

class LeadQualificationState(TypedDict):
    company_name: str
    research_data: Dict[str, Any]
    lead_analysis: str
    lead_score: int
    route_decision: str
    qualification_status: str
    qualification_error: str
    qualification_timestamp: str

class ContentCreationState(TypedDict):
    topic: str
    research_data: Dict[str, Any]
    outline: str
    content: str
    seo_optimized: str
    creation_status: str
    creation_error: str
    creation_timestamp: str

# Node Types for LangGraph
class LangGraphNode:
    def __init__(self, name: str, node_type: str):
        self.name = name
        self.type = node_type
        self.config = {}

# Workflow Types
class LangGraphWorkflow:
    def __init__(self, name: str, workflow_type: str):
        self.name = name
        self.type = workflow_type
        self.nodes = []
        self.edges = []
        self.state_type = None

# Execution Results
class WorkflowExecutionResult:
    def __init__(self):
        self.success: bool = False
        self.data: Dict[str, Any] = {}
        self.error: str = ""
        self.execution_time: float = 0.0
        self.timestamp: str = ""
        self.workflow_type: str = "" 