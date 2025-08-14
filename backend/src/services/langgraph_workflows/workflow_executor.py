from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
import json
from datetime import datetime
import uuid

from ..langgraph_nodes.workflow_nodes import LangGraphWorkflowNodes
from ..node_dispatcher import NodeDispatcher


class LangGraphWorkflowExecutor:
    def __init__(self):
        self.nodes = LangGraphWorkflowNodes()
        self.dispatcher = NodeDispatcher(self.nodes)
        self.memory = MemorySaver()
    
    def resolve_data_reference(self, reference: str, state: Dict[str, Any]) -> Any:
        """Resolve data references like 'node2.post_data' or 'ai_agent_1.output'.
        - If format is 'nodeId.field', first try node_results[nodeId][field], then top-level state[field]
        - If plain 'field', return state.get(field)
        """
        try:
            if '.' in reference:
                parts = reference.split('.')
                if len(parts) == 2:
                    node_id_ref, field_name = parts
                    # Try node-scoped result first
                    node_results = state.get('node_results', {}) or {}
                    if node_id_ref in node_results and isinstance(node_results[node_id_ref], dict):
                        candidate = node_results[node_id_ref].get(field_name)
                        if candidate is not None:
                            return candidate
                    # Fallback to top-level state
                    return state.get(field_name)
                else:
                    print(f"Warning: Invalid reference format: {reference}")
                    return None
            else:
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
        merged_state = current_state.copy()
        merged_state.update(node_result)
        if 'node_results' not in merged_state:
            merged_state['node_results'] = {}
        merged_state['node_results'][node_id] = node_result
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
    
    def _apply_edge_data_mappings(self, state: Dict[str, Any], edges: List[Dict[str, Any]], current_node_id: str) -> Dict[str, Any]:
        """Apply data_mapping from incoming edges to the current node's input state."""
        if not edges:
            return state
        updated = state.copy()
        for edge in edges:
            if edge.get('target') != current_node_id:
                continue
            mapping = edge.get('data_mapping') or {}
            if not isinstance(mapping, dict):
                continue
            for target_field, source_ref in mapping.items():
                resolved = self.resolve_data_reference(str(source_ref), state)
                if resolved is not None:
                    updated[target_field] = resolved
        return updated
    
    def build_workflow(self, workflow_data: Dict[str, Any]) -> StateGraph:
        """Build a LangGraph workflow from frontend workflow data"""
        try:
            workflow = StateGraph(Dict[str, Any])
            nodes_data = workflow_data.get('nodes', [])
            edges_data = workflow_data.get('edges', [])
            node_functions: Dict[str, Any] = {}
            for node in nodes_data:
                node_id = node['id']
                node_type = node['type']
                # Map node types to functions via dispatcher (OCP)
                node_functions[node_id] = self.dispatcher.get_executor(node_type)
                workflow.add_node(node_id, node_functions[node_id])
            # Add edges to the graph
            for edge in edges_data:
                source = edge['source']
                target = edge['target']
                if source in node_functions and target in node_functions:
                    workflow.add_edge(source, target)
            # Entry/exit points
            if nodes_data:
                entry_node = nodes_data[0]['id']
                workflow.set_entry_point(entry_node)
            else:
                workflow.add_node("start", lambda state: state)
                workflow.set_entry_point("start")
            if nodes_data:
                exit_node = nodes_data[-1]['id']
                workflow.add_edge(exit_node, END)
            else:
                workflow.add_edge("start", END)
            return workflow.compile(checkpointer=self.memory)
        except Exception as e:
            print(f"Error building workflow: {e}")
            return self._create_default_workflow()
    
    def execute_workflow(self, workflow_data: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow using LangGraph"""
        try:
            print(f"Executing workflow: {workflow_data.get('name', 'Unknown')}")
            print(f"Input data keys: {list(input_data.keys())}")
            initial_state = {
                'workflow_id': str(uuid.uuid4()),
                'start_time': datetime.now().isoformat(),
                'input_data': input_data,
                'workflow_name': workflow_data.get('name', 'Unknown'),
                'nodes_executed': [],
                'node_results': {}
            }
            current_state = initial_state.copy()
            execution_order = self._get_execution_order(workflow_data['nodes'], workflow_data['edges'])
            print(f"Execution order: {execution_order}")
            for node_id in execution_order:
                print(f"\nExecuting node: {node_id}")
                node_data = next((node for node in workflow_data['nodes'] if node['id'] == node_id), None)
                if not node_data:
                    print(f"Warning: Node {node_id} not found in workflow")
                    continue
                current_state['current_node'] = node_id
                current_state['node_config'] = node_data.get('data', {}).get('config', {})
                # Apply data mappings from incoming edges to produce the node's input view
                node_input_state = self._apply_edge_data_mappings(current_state, workflow_data.get('edges', []), node_id)
                # Execute the node
                node_result = self.execute_node(
                    node_data['type'],
                    node_data.get('data', {}).get('config', {}),
                    node_input_state,
                    workflow_data.get('edges', []),
                    node_id
                )
                current_state = self.merge_node_result(current_state, node_result, node_id)
                print(f"Node {node_id} completed with status: {node_result.get('status', 'unknown')}")
                print(f"State after {node_id}: {list(current_state.keys())}")
                if 'node_results' in current_state:
                    print(f"  Node results: {list(current_state['node_results'].keys())}")
            result = {
                'workflow_id': initial_state['workflow_id'],
                'start_time': initial_state['start_time'],
                'input_data': input_data,
                'current_node': None,
                'status': 'completed',
                'execution_id': initial_state['workflow_id'],
                'end_time': datetime.now().isoformat()
            }
            essential_keys = ['result', 'output', 'content', 'status', 'timestamp', 'image_url', 'social_data', 'instagram_post']
            for key in essential_keys:
                if key in current_state:
                    value = current_state[key]
                    if isinstance(value, (str, int, float, bool, type(None))):
                        result[key] = value
                    elif isinstance(value, dict):
                        result[key] = {k: (v if isinstance(v, (str, int, float, bool, type(None))) else str(v)) for k, v in value.items()}
                    elif isinstance(value, list):
                        result[key] = [(item if isinstance(item, (str, int, float, bool, type(None))) else str(item)) for item in value]
                    else:
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
    
    def execute_node(self, node_type: str, node_config: Dict[str, Any], input_data: Dict[str, Any], edges: Optional[List[Dict[str, Any]]] = None, current_node_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute a single node. Optional edges/current_node_id for mapping; kept for backward compatibility."""
        try:
            config = node_config if isinstance(node_config, dict) else {}
            state = input_data.copy()
            state.update({
                'node_type': node_type,
                'start_time': datetime.now().isoformat(),
                **config
            })
            print(f"Executing {node_type} with config: {config}")
            print(f"Input state keys: {list(input_data.keys())}")
            # Dispatch
            executor = self.dispatcher.get_executor(node_type)
            # Special-case adornments for known nodes
            if node_type == 'aiAgent':
                state['prompt'] = config.get('prompt', '')
                state['task'] = config.get('task', 'generate')
                state['topic'] = config.get('topic', 'content generation')
            elif node_type == 'data':
                state['input_source'] = config.get('input', '')
                state['output_name'] = config.get('output', 'post_data')
            elif node_type == 'instagram_post':
                import os
                state['platform'] = 'instagram'
                state['access_token'] = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
                state['post'] = config.get('post', '')
                if state.get('post'):
                    resolved_content = self.resolve_data_reference(state['post'], input_data)
                    if resolved_content is not None:
                        state['content'] = resolved_content
                    else:
                        state['content'] = state.get('post', '')
            elif node_type == 'textOverlay':
                state['overlay_text'] = config.get('overlay_text', state.get('overlay_text', ''))
                state['image_url'] = config.get('image_url', state.get('image_url', ''))
                state['image_width'] = config.get('image_width', state.get('image_width', 1080))
                state['image_height'] = config.get('image_height', state.get('image_height', 1080))
            # Execute
            result = executor(state)
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
        workflow.add_node("default", self.nodes.ai_agent_node)
        workflow.set_entry_point("default")
        workflow.add_edge("default", END)
        return workflow.compile(checkpointer=self.memory)
    
    def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """Get the status of a workflow execution"""
        try:
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
        dependencies: Dict[str, List[str]] = {}
        for node in nodes_data:
            dependencies[node['id']] = []
        for edge in edges_data:
            source = edge['source']
            target = edge['target']
            if target in dependencies:
                dependencies[target].append(source)
        return dependencies
    
    def _topological_sort(self, dependencies: Dict[str, List[str]]) -> List[str]:
        """Perform topological sort to determine execution order"""
        in_degree: Dict[str, int] = {}
        for node, deps in dependencies.items():
            in_degree[node] = len(deps)
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result: List[str] = []
        while queue:
            current = queue.pop(0)
            result.append(current)
            for node, deps in dependencies.items():
                if current in deps:
                    in_degree[node] -= 1
                    if in_degree[node] == 0:
                        queue.append(node)
        return result 