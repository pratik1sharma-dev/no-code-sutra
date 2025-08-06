from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
import json
from datetime import datetime
import uuid

from ..langgraph_nodes.workflow_nodes import LangGraphWorkflowNodes

class LangGraphWorkflowExecutor:
    def __init__(self):
        self.nodes = LangGraphWorkflowNodes()
        self.memory = MemorySaver()
    
    def build_workflow(self, workflow_data: Dict[str, Any]) -> StateGraph:
        """Build a LangGraph workflow from frontend workflow data"""
        try:
            # Create state graph
            workflow = StateGraph(Dict[str, Any])
            
            # Add nodes to the graph
            nodes_data = workflow_data.get('nodes', [])
            edges_data = workflow_data.get('edges', [])
            
            # Create a mapping of node IDs to node functions
            node_functions = {}
            
            for node in nodes_data:
                node_id = node['id']
                node_type = node['type']
                
                # Map node types to functions
                if node_type == 'aiAgent':
                    node_functions[node_id] = self.nodes.ai_agent_node
                elif node_type == 'email':
                    node_functions[node_id] = self.nodes.email_node
                elif node_type == 'slack':
                    node_functions[node_id] = self.nodes.slack_node
                elif node_type == 'data':
                    node_functions[node_id] = self.nodes.data_node
                elif node_type == 'condition':
                    node_functions[node_id] = self.nodes.condition_node
                elif node_type == 'delay':
                    node_functions[node_id] = self.nodes.delay_node
                elif node_type == 'schedule':
                    node_functions[node_id] = self.nodes.schedule_node
                elif node_type == 'blogWriter':
                    node_functions[node_id] = self.nodes.blog_writer_node
                elif node_type == 'socialMedia':
                    node_functions[node_id] = self.nodes.social_media_node
                elif node_type == 'imageGenerator':
                    node_functions[node_id] = self.nodes.image_generator_node
                elif node_type == 'seoOptimizer':
                    node_functions[node_id] = self.nodes.seo_optimizer_node
                else:
                    # Default to AI agent for unknown types
                    node_functions[node_id] = self.nodes.ai_agent_node
                
                # Add node to graph
                workflow.add_node(node_id, node_functions[node_id])
            
            # Add edges to the graph
            for edge in edges_data:
                source = edge['source']
                target = edge['target']
                
                if source in node_functions and target in node_functions:
                    workflow.add_edge(source, target)
            
            # Set entry point (first node or a default)
            if nodes_data:
                entry_node = nodes_data[0]['id']
                workflow.set_entry_point(entry_node)
            else:
                # Create a default entry point
                workflow.add_node("start", lambda state: state)
                workflow.set_entry_point("start")
            
            # Set exit point
            if nodes_data:
                exit_node = nodes_data[-1]['id']
                workflow.add_edge(exit_node, END)
            else:
                workflow.add_edge("start", END)
            
            return workflow.compile(checkpointer=self.memory)
            
        except Exception as e:
            print(f"Error building workflow: {e}")
            # Return a simple default workflow
            return self._create_default_workflow()
    
    def execute_workflow(self, workflow_data: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow with given input data"""
        try:
            # Build the workflow
            compiled_workflow = self.build_workflow(workflow_data)
            
            # Prepare initial state
            initial_state = {
                'workflow_id': str(uuid.uuid4()),
                'start_time': datetime.now().isoformat(),
                'input_data': input_data,
                'nodes_executed': [],
                'current_node': None,
                'results': {},
                **input_data  # Include input data in state
            }
            
            # Execute the workflow
            config = {"configurable": {"thread_id": initial_state['workflow_id']}}
            result = compiled_workflow.invoke(initial_state, config)
            
            # Add execution metadata
            result['execution_id'] = initial_state['workflow_id']
            result['end_time'] = datetime.now().isoformat()
            result['status'] = 'completed'
            
            return result
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'execution_id': str(uuid.uuid4()),
                'end_time': datetime.now().isoformat()
            }
    
    def execute_node(self, node_type: str, node_config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single node"""
        try:
            # Prepare state
            state = {
                'node_id': str(uuid.uuid4()),
                'node_type': node_type,
                'start_time': datetime.now().isoformat(),
                **input_data,
                **node_config
            }
            
            # Execute node based on type
            if node_type == 'aiAgent':
                result = self.nodes.ai_agent_node(state)
            elif node_type == 'email':
                result = self.nodes.email_node(state)
            elif node_type == 'slack':
                result = self.nodes.slack_node(state)
            elif node_type == 'data':
                result = self.nodes.data_node(state)
            elif node_type == 'condition':
                result = self.nodes.condition_node(state)
            elif node_type == 'delay':
                result = self.nodes.delay_node(state)
            elif node_type == 'schedule':
                result = self.nodes.schedule_node(state)
            elif node_type == 'blogWriter':
                result = self.nodes.blog_writer_node(state)
            elif node_type == 'socialMedia':
                result = self.nodes.social_media_node(state)
            elif node_type == 'imageGenerator':
                result = self.nodes.image_generator_node(state)
            elif node_type == 'seoOptimizer':
                result = self.nodes.seo_optimizer_node(state)
            else:
                result = self.nodes.ai_agent_node(state)
            
            # Add execution metadata
            result['end_time'] = datetime.now().isoformat()
            result['node_type'] = node_type
            
            return result
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'node_type': node_type,
                'end_time': datetime.now().isoformat()
            }
    
    def _create_default_workflow(self) -> StateGraph:
        """Create a default workflow for fallback"""
        workflow = StateGraph(Dict[str, Any])
        
        # Add a simple AI agent node
        workflow.add_node("default", self.nodes.ai_agent_node)
        workflow.set_entry_point("default")
        workflow.add_edge("default", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """Get the status of a workflow execution"""
        try:
            # In a real implementation, you'd query the memory/checkpoint system
            # For now, return a simple status
            return {
                'execution_id': execution_id,
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'execution_id': execution_id,
                'status': 'unknown',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            } 