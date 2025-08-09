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
    
    def resolve_data_reference(self, reference: str, state: Dict[str, Any]) -> Any:
        """Resolve data references like 'node2.post_data' or direct field names"""
        try:
            if '.' in reference:
                # Handle "node2.post_data" format
                parts = reference.split('.')
                if len(parts) == 2:
                    field_name = parts[1]
                    if field_name in state:
                        return state[field_name]
                    else:
                        print(f"Warning: Field '{field_name}' not found in state. Available keys: {list(state.keys())}")
                        return None
                else:
                    print(f"Warning: Invalid reference format: {reference}")
                    return None
            else:
                # Direct field reference
                return state.get(reference, None)
        except Exception as e:
            print(f"Error resolving data reference '{reference}': {e}")
            return None
    
    def standardize_node_output(self, result: Dict[str, Any], node_id: str, node_type: str) -> Dict[str, Any]:
        """Standardize node output format for consistent state management"""
        standardized = {
            'node_id': node_id,
            'node_type': node_type,
            'status': result.get('status', 'unknown'),
            'timestamp': result.get('timestamp', datetime.now().isoformat()),
            'output': result.get('result', result.get('output', result.get('content', ''))),
            'metadata': {}
        }
        
        # Add all other fields as metadata
        for key, value in result.items():
            if key not in ['node_id', 'node_type', 'status', 'timestamp', 'output']:
                standardized['metadata'][key] = value
        
        return standardized
    
    def merge_node_result(self, current_state: Dict[str, Any], node_result: Dict[str, Any], node_id: str) -> Dict[str, Any]:
        """Intelligently merge node result with current state"""
        # Create a copy to avoid modifying the original
        merged_state = current_state.copy()
        
        # Add node result to the merged state
        merged_state.update(node_result)
        
        # Store node result in a structured way
        if 'node_results' not in merged_state:
            merged_state['node_results'] = {}
        
        merged_state['node_results'][node_id] = node_result
        
        # Update execution tracking
        if 'nodes_executed' not in merged_state:
            merged_state['nodes_executed'] = []
        
        merged_state['nodes_executed'].append({
            'node_id': node_id,
            'node_type': node_result.get('node_type', 'unknown'),
            'status': node_result.get('status', 'unknown'),
            'execution_time': node_result.get('timestamp', ''),
            'result': node_result
        })
        
        return merged_state
    
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
                elif node_type == 'instagram_post':
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
        """Execute a workflow using LangGraph"""
        try:
            print(f"Executing workflow: {workflow_data.get('name', 'Unknown')}")
            print(f"Input data keys: {list(input_data.keys())}")
            
            # Initialize state
            initial_state = {
                'workflow_id': str(uuid.uuid4()),
                'start_time': datetime.now().isoformat(),
                'input_data': input_data,
                'workflow_name': workflow_data.get('name', 'Unknown'),
                'nodes_executed': [],
                'node_results': {}
            }
            
            current_state = initial_state.copy()
            
            # Get execution order
            execution_order = self._get_execution_order(workflow_data['nodes'], workflow_data['edges'])
            print(f"Execution order: {execution_order}")
            
            # Execute nodes in order
            for node_id in execution_order:
                print(f"\nExecuting node: {node_id}")
                
                # Find node data
                node_data = next((node for node in workflow_data['nodes'] if node['id'] == node_id), None)
                if not node_data:
                    print(f"Warning: Node {node_id} not found in workflow")
                    continue
                
                # Update current state
                current_state['current_node'] = node_id
                current_state['node_config'] = node_data.get('data', {}).get('config', {})
                
                # Execute the node
                node_result = self.execute_node(
                    node_data['type'], 
                    node_data.get('data', {}).get('config', {}), 
                    current_state
                )
                
                # Update state with node result using improved merging
                current_state = self.merge_node_result(current_state, node_result, node_id)
                
                print(f"Node {node_id} completed with status: {node_result.get('status', 'unknown')}")
                print(f"State after {node_id}: {list(current_state.keys())}")
                if 'node_results' in current_state:
                    print(f"  Node results: {list(current_state['node_results'].keys())}")
            
            # Prepare final result - ensure JSON serializable
            result = {
                'workflow_id': initial_state['workflow_id'],
                'start_time': initial_state['start_time'],
                'input_data': input_data,
                'current_node': None,  # All nodes completed
                'status': 'completed',
                'execution_id': initial_state['workflow_id'],
                'end_time': datetime.now().isoformat()
            }
            
            # Include final state data but ensure it's serializable
            for key, value in current_state.items():
                if key not in ['workflow_id', 'start_time', 'input_data', 'current_node', 'status', 'execution_id', 'end_time']:
                    # Ensure the value is JSON serializable
                    if isinstance(value, (str, int, float, bool, type(None))):
                        result[key] = value
                    elif isinstance(value, list):
                        # Convert list items to serializable format
                        serializable_list = []
                        for item in value:
                            if isinstance(item, dict):
                                serializable_list.append(self._make_serializable(item))
                            else:
                                serializable_list.append(str(item) if not isinstance(item, (str, int, float, bool, type(None))) else item)
                        result[key] = serializable_list
                    elif isinstance(value, dict):
                        result[key] = self._make_serializable(value)
                    else:
                        # Convert to string if not serializable
                        result[key] = str(value)
            
            return result
            
        except Exception as e:
            print(f"Error executing workflow: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'execution_id': str(uuid.uuid4()),
                'end_time': datetime.now().isoformat(),
                'nodes_executed': [],
                'results': {}
            }
    
    def execute_node(self, node_type: str, node_config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single node"""
        try:
            # Extract configuration from the workflow node structure
            config = node_config.get('config', {})
            
            # Prepare state with proper configuration - preserve existing state
            state = input_data.copy()
            state.update({
                'node_type': node_type,
                'start_time': datetime.now().isoformat(),
                **config       # Include node-specific configuration
            })
            
            print(f"Executing {node_type} with config: {config}")
            print(f"Input state keys: {list(input_data.keys())}")
            
            # Execute node based on type
            if node_type == 'aiAgent':
                # Extract task and topic from config
                state['task'] = config.get('task', 'research')
                state['topic'] = config.get('topic', 'general research')
                result = self.nodes.ai_agent_node(state)
            elif node_type == 'email':
                result = self.nodes.email_node(state)
            elif node_type == 'slack':
                result = self.nodes.slack_node(state)
            elif node_type == 'data':
                # Handle data node configuration
                state['input_source'] = config.get('input', '')
                state['output_name'] = config.get('output', 'post_data')
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
            elif node_type == 'instagram_post':
                # Handle Instagram post configuration
                state['platform'] = 'instagram'
                state['access_token'] = config.get('access_token', '')
                state['post'] = config.get('post', '')
                
                # Use improved data reference resolution
                if state.get('post'):
                    resolved_content = self.resolve_data_reference(state['post'], input_data)
                    if resolved_content is not None:
                        state['content'] = resolved_content
                        print(f"Resolved content from '{state['post']}': {str(resolved_content)[:100]}...")
                    else:
                        state['content'] = state.get('post', '')
                        print(f"Using direct post content: {state['content']}")
                else:
                    state['content'] = ''
                
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
            
            print(f"Node {node_type} result: {result.get('status', 'unknown')}")
            if 'result' in result:
                print(f"Content preview: {str(result['result'])[:100]}...")
            
            return result
            
        except Exception as e:
            print(f"Error executing node {node_type}: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'node_type': node_type,
                'end_time': datetime.now().isoformat()
            }
    
    def _get_execution_order(self, nodes_data: List[Dict], edges_data: List[Dict]) -> List[str]:
        """Get the execution order of nodes using topological sort"""
        dependencies = self._build_dependency_graph(nodes_data, edges_data)
        return self._topological_sort(dependencies)
    
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
    
    def _build_dependency_graph(self, nodes_data: List[Dict], edges_data: List[Dict]) -> Dict[str, List[str]]:
        """Build a dependency graph from nodes and edges"""
        dependencies = {}
        
        # Initialize all nodes with no dependencies
        for node in nodes_data:
            dependencies[node['id']] = []
        
        # Add dependencies from edges
        for edge in edges_data:
            source = edge['source']
            target = edge['target']
            if target in dependencies:
                dependencies[target].append(source)
        
        return dependencies
    
    def _topological_sort(self, dependencies: Dict[str, List[str]]) -> List[str]:
        """Perform topological sort to determine execution order"""
        # Kahn's algorithm
        in_degree = {}
        for node, deps in dependencies.items():
            in_degree[node] = len(deps)
        
        # Find nodes with no dependencies
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Reduce in-degree for dependent nodes
            for node, deps in dependencies.items():
                if current in deps:
                    in_degree[node] -= 1
                    if in_degree[node] == 0:
                        queue.append(node)
        
        return result 

    def _make_serializable(self, obj: Any) -> Any:
        """Convert an object to JSON serializable format"""
        if isinstance(obj, dict):
            serializable_dict = {}
            for key, value in obj.items():
                if isinstance(value, (str, int, float, bool, type(None))):
                    serializable_dict[key] = value
                elif isinstance(value, list):
                    serializable_dict[key] = [self._make_serializable(item) for item in value]
                elif isinstance(value, dict):
                    serializable_dict[key] = self._make_serializable(value)
                else:
                    serializable_dict[key] = str(value)
            return serializable_dict
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        else:
            return str(obj) if not isinstance(obj, (str, int, float, bool, type(None))) else obj 