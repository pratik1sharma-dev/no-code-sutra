from typing import Dict, Any
from src.services.langgraph_nodes.ai_nodes import SimpleAIWorkflowNodes
from src.workflow_types.workflow import ResearchState, LeadQualificationState

class SimpleWorkflows:
    def __init__(self):
        self.ai_nodes = SimpleAIWorkflowNodes()
    
    def execute_research_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a simple research workflow"""
        try:
            # Execute research node
            result = self.ai_nodes.research_company(input_data)
            return {
                "success": True,
                "data": result,
                "workflow_type": "research"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_type": "research"
            }
    
    def execute_lead_qualification_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a complete lead qualification workflow"""
        try:
            # Execute all nodes in sequence
            state = input_data.copy()
            
            # Step 1: Research
            state = self.ai_nodes.research_company(state)
            if state.get('research_status') == 'failed':
                raise Exception(f"Research failed: {state.get('research_error')}")
            
            # Step 2: Analyze
            state = self.ai_nodes.analyze_lead(state)
            if state.get('qualification_status') == 'failed':
                raise Exception(f"Analysis failed: {state.get('qualification_error')}")
            
            # Step 3: Score
            state = self.ai_nodes.score_lead(state)
            if state.get('qualification_status') == 'failed':
                raise Exception(f"Scoring failed: {state.get('qualification_error')}")
            
            # Step 4: Route
            state = self.ai_nodes.route_lead(state)
            if state.get('qualification_status') == 'failed':
                raise Exception(f"Routing failed: {state.get('qualification_error')}")
            
            return {
                "success": True,
                "data": state,
                "workflow_type": "lead_qualification"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_type": "lead_qualification"
            }

# Workflow factory
class WorkflowFactory:
    def __init__(self):
        self.workflows = SimpleWorkflows()
    
    def execute_workflow(self, workflow_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow with input data"""
        try:
            if workflow_type == "research":
                return self.workflows.execute_research_workflow(input_data)
            elif workflow_type == "lead_qualification":
                return self.workflows.execute_lead_qualification_workflow(input_data)
            else:
                raise ValueError(f"Unknown workflow type: {workflow_type}")
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "workflow_type": workflow_type
            } 