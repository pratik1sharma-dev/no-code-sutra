from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
import json
from datetime import datetime
import uuid
import logging

from ..node_dispatcher import NodeDispatcher

# Configure structured logging with environment-based level
import os
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)


class LangGraphWorkflowExecutor:
    def __init__(self):
        self.dispatcher = NodeDispatcher()
        self.memory = MemorySaver()
    
    def resolve_data_reference(self, reference: str, state: Dict[str, Any]) -> Any:
        """Resolve data references like 'node2.post_data' or 'ai_agent_1.output'.
        - If format is 'nodeId.field', first try node_results[nodeId][field], then top-level state[field]
        - If plain 'field', return state.get(field)
        """
        try:
            if '.' in reference:
                parts = reference.split('.')
                if len(parts) >= 2:
                    node_id_ref = parts[0]
                    field_path = parts[1:]
                    
                    # Try node-scoped result first
                    node_results = state.get('node_results', {}) or {}
                    if node_id_ref in node_results and isinstance(node_results[node_id_ref], dict):
                        # Navigate nested field path
                        candidate = node_results[node_id_ref]
                        for field in field_path:
                            if isinstance(candidate, dict) and field in candidate:
                                candidate = candidate[field]
                            else:
                                candidate = None
                                break
                        if candidate is not None:
                            return candidate
                    
                    # Fallback to top-level state for simple field access
                    if len(field_path) == 1:
                        return state.get(field_path[0])
                    return None
                else:
                    logger.warning(f"Invalid reference format: {reference}")
            return None
        else:
            return state.get(reference, None)
    except Exception as e:
        logger.error(f"Error resolving data reference '{reference}': {e}")
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
            logger.error(f"Error building workflow: {e}", exc_info=True)
            return self._create_default_workflow()
    
    def execute_workflow(self, workflow_data: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow using LangGraph"""
        try:
            workflow_id = str(uuid.uuid4())
            logger.info(f"🚀 Starting workflow execution - ID: {workflow_id}, Name: {workflow_data.get('name', 'Unknown')}")
            logger.info(f"📥 Input data keys: {list(input_data.keys())}")
            initial_state = {
                'workflow_id': workflow_id,
                'start_time': datetime.now().isoformat(),
                'input_data': input_data,
                'workflow_name': workflow_data.get('name', 'Unknown'),
                'nodes_executed': [],
                'node_results': {}
            }
            current_state = initial_state.copy()
            execution_order = self._get_execution_order(workflow_data['nodes'], workflow_data['edges'])
            logger.info(f"📋 Execution order: {execution_order}")
            for node_id in execution_order:
                logger.info(f"🔄 Executing node: {node_id}")
                node_data = next((node for node in workflow_data['nodes'] if node['id'] == node_id), None)
                if not node_data:
                    logger.warning(f"Node {node_id} not found in workflow")
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
                status = node_result.get('status', 'unknown')
                if status == 'failed':
                    logger.error(f"❌ Node {node_id} failed: {node_result.get('error', 'Unknown error')}")
                else:
                    logger.info(f"✅ Node {node_id} completed with status: {status}")
                logger.info(f"📊 State keys after {node_id}: {list(current_state.keys())}")
                if 'node_results' in current_state:
                    logger.info(f"📋 Node results available: {list(current_state['node_results'].keys())}")
            # Check if any nodes failed
            failed_nodes = [node for node in current_state.get('nodes_executed', []) if node.get('status') == 'failed']
            has_failures = len(failed_nodes) > 0
            
            if has_failures:
                logger.warning(f"⚠️ Workflow {workflow_id} completed with {len(failed_nodes)} failed nodes")
                for failed_node in failed_nodes:
                    logger.error(f"Failed node details - ID: {failed_node.get('node_id')}, Error: {failed_node.get('result', {}).get('error', 'Unknown')}")
            else:
                logger.info(f"🎉 Workflow {workflow_id} completed successfully")
            
            # Create clean result without circular references
            result = {
                'workflow_id': str(initial_state['workflow_id']),
                'start_time': str(initial_state['start_time']),
                'input_data': self._sanitize_for_json(input_data),
                'current_node': None,
                'status': 'failed' if has_failures else 'completed',
                'execution_id': str(initial_state['workflow_id']),
                'end_time': datetime.now().isoformat(),
                'failed_nodes': self._sanitize_for_json(failed_nodes) if has_failures else [],
                'error_details': [{'node_id': str(node.get('node_id', '')), 'error': str(node.get('result', {}).get('error', 'Unknown error'))} for node in failed_nodes] if has_failures else []
            }
            essential_keys = ['result', 'output', 'content', 'status', 'timestamp', 'image_url', 'social_data', 'instagram_post']
            for key in essential_keys:
                if key in current_state:
                    result[key] = self._sanitize_for_json(current_state[key])
            return result
        except Exception as e:
            logger.error(f"💥 Critical workflow execution error: {e}", exc_info=True)
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
            logger.info(f"🔧 Executing {node_type} node - ID: {current_node_id or 'unknown'}")
            logger.info(f"⚙️ Node config: {config}")
            logger.info(f"📥 Input state keys: {list(input_data.keys())}")
            executor = self.dispatcher.get_executor(node_type)
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
                # Don't set access_token here - let the social media node get it from stored credentials
                state['access_token'] = ''  # Empty to force using stored token
                state['user_id'] = 'default_user'  # Add user_id to state
                state['post'] = config.get('post', '')
                if state.get('post'):
                    resolved_content = self.resolve_data_reference(state['post'], input_data)
                    if resolved_content is not None:
                        state['content'] = resolved_content
                    else:
                        state['content'] = state.get('post', '')
            elif node_type == 'imageGenerator':
                state['structured_data'] = config.get('structured_data', state.get('structured_data', {}))
                state['prompt'] = config.get('prompt', state.get('prompt', ''))
                state['style'] = config.get('style', state.get('style', 'modern'))
                state['user_image_url'] = config.get('user_image_url', state.get('user_image_url', ''))
            elif node_type == 'textOverlay':
                # Get structured_data from previous nodes (AI agent output)
                state['structured_data'] = state.get('structured_data', {})
                state['overlay_text'] = config.get('overlay_text', state.get('overlay_text', ''))
                state['image_url'] = config.get('image_url', state.get('image_url', ''))
                state['image_width'] = config.get('image_width', state.get('image_width', 1080))
                state['image_height'] = config.get('image_height', state.get('image_height', 1080))
                
                # Canva template configuration (default to True for testing)
                state['canva_template_id'] = config.get('canva_template_id', state.get('canva_template_id', 'EAGFcgTrfLo'))
                state['use_canva_template'] = config.get('use_canva_template', state.get('use_canva_template', True))
                state['export_format'] = config.get('export_format', state.get('export_format', 'png'))
                state['export_width'] = config.get('export_width', state.get('export_width', 1080))
                state['export_height'] = config.get('export_height', state.get('export_height', 1080))
            result = executor(state)
            result['end_time'] = datetime.now().isoformat()
            result['node_type'] = node_type
            
            # Enhanced logging with node context
            status = result.get('status', 'unknown')
            node_id = current_node_id or 'unknown'
            
            if status == 'failed':
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"❌ Node {node_type}[{node_id}] failed: {error_msg}")
            elif status == 'completed':
                logger.info(f"✅ Node {node_type}[{node_id}] completed successfully")
            else:
                logger.info(f"🔄 Node {node_type}[{node_id}] status: {status}")
                
            if 'result' in result:
                content_preview = str(result['result'])[:100]
                logger.info(f"📄 Content preview for {node_type}[{node_id}]: {content_preview}...")
                
            return result
        except Exception as e:
            node_id = current_node_id or 'unknown'
            logger.error(f"💥 Exception in node {node_type}[{node_id}]: {e}", exc_info=True)
            return {
                'status': 'failed',
                'error': str(e),
                'node_type': node_type,
                'node_id': node_id,
                'end_time': datetime.now().isoformat()
            }
    
    def _get_execution_order(self, nodes_data: List[Dict], edges_data: List[Dict]) -> List[str]:
        """Get the execution order of nodes using topological sort"""
        dependencies = self._build_dependency_graph(nodes_data, edges_data)
        return self._topological_sort(dependencies)
    
    def _create_default_workflow(self) -> StateGraph:
        """Create a default workflow for fallback"""
        workflow = StateGraph(Dict[str, Any])
        from ..nodes import ai_agent as _ai
        workflow.add_node("default", _ai.execute)
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
    
    def _sanitize_for_json(self, obj: Any, max_depth: int = 5, current_depth: int = 0) -> Any:
        """Sanitize objects for JSON serialization, preventing circular references"""
        if current_depth > max_depth:
            return str(obj)
        
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {str(k): self._sanitize_for_json(v, max_depth, current_depth + 1) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._sanitize_for_json(item, max_depth, current_depth + 1) for item in obj]
        else:
            return str(obj) 