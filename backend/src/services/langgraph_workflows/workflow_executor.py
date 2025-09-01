from typing import Dict, Any, List, Optional
import os
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
try:
    # Prefer a durable SQL-based checkpointer when configured
    from langgraph.checkpoint.sqlite import SqliteSaver  # type: ignore
except Exception:  # pragma: no cover
    SqliteSaver = None  # type: ignore
try:
    # Optional Postgres checkpointer (if available in installed langgraph version)
    from langgraph.checkpoint.postgres import PostgresSaver  # type: ignore
except Exception:  # pragma: no cover
    PostgresSaver = None  # type: ignore
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
        # Choose checkpointer: durable sqlite if configured, else in-memory
        checkpoint_backend = os.getenv('CHECKPOINT_BACKEND', 'memory').lower()
        if checkpoint_backend == 'postgres' and PostgresSaver is not None:
            pg_url = os.getenv('CHECKPOINT_POSTGRES_URL') or os.getenv('DATABASE_URL')
            if not pg_url:
                print("LangGraph postgres checkpointer requested but no URL provided; falling back to memory")
                self.memory = MemorySaver()
            else:
                try:
                    self.memory = PostgresSaver(pg_url)  # type: ignore
                    print("LangGraph checkpointer: postgres")
                except Exception as e:
                    print(f"LangGraph postgres checkpointer init failed: {e}; falling back to memory")
                    self.memory = MemorySaver()
        elif checkpoint_backend == 'sqlite' and SqliteSaver is not None:
            db_path = os.getenv('CHECKPOINT_SQLITE_PATH', '/workspace/.checkpoints/langgraph_checkpoints.sqlite')
            # Ensure directory exists
            try:
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
            except Exception:
                pass
            self.memory = SqliteSaver(db_path)
            print(f"LangGraph checkpointer: sqlite at {db_path}")
        else:
            self.memory = MemorySaver()
            if checkpoint_backend != 'memory':
                print(f"LangGraph checkpointer fallback to memory (requested: {checkpoint_backend})")
    
    def resolve_data_reference(self, reference: str, state: Dict[str, Any]) -> Any:
        """Resolve data references like 'node2.post_data' or 'ai_agent_1.output'.
        - If format is 'nodeId.field', first try node_results[nodeId][field], then top-level state[field]
        - If format is 'input.something', read from state['input_data']
        - If plain 'field', return state.get(field)
        """
        try:
            if '.' in reference:
                parts = reference.split('.')
                if len(parts) >= 2:
                    node_id_ref = parts[0]
                    field_path = parts[1:]
                    # Special-case: input.* reads initial input_data
                    if node_id_ref == 'input':
                        input_data = state.get('input_data', {}) or {}
                        if isinstance(input_data, dict):
                            # only support single-segment access for input.*
                            return input_data.get(field_path[0]) if field_path else None
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
    
    def _sanitize_for_json(self, value: Any) -> Any:
        """Recursively sanitize values so they are JSON-serializable."""
        try:
            # Primitive types pass through
            if isinstance(value, (str, int, float, bool)) or value is None:
                return value
            # datetime -> ISO string
            from datetime import datetime as _dt
            if isinstance(value, _dt):
                return value.isoformat()
            # dict -> sanitize keys/values
            if isinstance(value, dict):
                return {str(k): self._sanitize_for_json(v) for k, v in value.items()}
            # list/tuple -> sanitize items
            if isinstance(value, (list, tuple)):
                return [self._sanitize_for_json(v) for v in value]
            # Fallback: string representation
            return str(value)
        except Exception:
            return str(value)
    
    
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
        """Build and compile a LangGraph workflow from frontend workflow data.
        - Wrap node executors to merge results back into state
        - Require explicit `entry`
        - Support optional `conditions` for conditional routing
        - Preserve declared linear edges and END
        """
        try:
            builder = StateGraph(Dict[str, Any])
            nodes_data = workflow_data.get('nodes', []) or []
            edges_data = workflow_data.get('edges', []) or []
            conditions_data = workflow_data.get('conditions', []) or []

            # Enforce no-backcompat schema: require entry + reads/writes
            entry_node = workflow_data.get('entry')
            if not entry_node:
                raise ValueError("Workflow must specify explicit 'entry' node id")
            for node in nodes_data:
                if 'reads' not in node or 'writes' not in node:
                    raise ValueError(f"Node {node.get('id')} must include 'reads' and 'writes' lists")

            # Precompute node configs and types
            node_config_by_id: Dict[str, Dict[str, Any]] = {}
            node_type_by_id: Dict[str, str] = {}
            node_reads_by_id: Dict[str, List[str]] = {}
            node_writes_by_id: Dict[str, List[str]] = {}
            for node in nodes_data:
                node_id = node['id']
                node_type = node['type']
                node_type_by_id[node_id] = node_type
                node_config_by_id[node_id] = (node.get('data', {}) or {}).get('config', {}) or {}
                node_reads_by_id[node_id] = node.get('reads', []) or []
                node_writes_by_id[node_id] = node.get('writes', []) or []

            # Wrapper to adapt executors to LangGraph state updates
            def make_node_wrapper(node_id: str):
                node_type = node_type_by_id.get(node_id, 'unknown')
                node_config = node_config_by_id.get(node_id, {})
                reads = node_reads_by_id.get(node_id, [])
                writes = node_writes_by_id.get(node_id, [])

                def _wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
                    # Build node input view from declared reads
                    node_input_state = state.copy()
                    for read_key in reads:
                        value = self.resolve_data_reference(str(read_key), state)
                        if value is not None:
                            # Assign to top-level by last segment name
                            key_name = str(read_key).split('.')[-1]
                            node_input_state[key_name] = value
                    start_ts = datetime.now()
                    # Execute the node
                    # Basic tracing: mark start
                    state['last_event'] = {
                        'type': 'node_start',
                        'node_id': node_id,
                        'node_type': node_type,
                        'timestamp': start_ts.isoformat()
                    }
                    node_result = self.execute_node(
                        node_type=node_type,
                        node_config=node_config,
                        input_data=node_input_state,
                        edges=edges_data,
                        current_node_id=node_id
                    )
                    end_ts = datetime.now()
                    duration_ms = int((end_ts - start_ts).total_seconds() * 1000)
                    # Merge back into state for downstream nodes
                    merged = self.merge_node_result(state, node_result, node_id)
                    # Validate declared writes exist in merged state
                    missing = []
                    for w in writes:
                        if w not in merged and (not merged.get('node_results', {}).get(node_id, {}).get(w)):
                            missing.append(w)
                    if missing:
                        raise ValueError(f"Node {node_id} did not produce declared writes: {missing}")
                    # Basic tracing: mark end
                    merged['last_event'] = {
                        'type': 'node_end',
                        'node_id': node_id,
                        'node_type': node_type,
                        'timestamp': end_ts.isoformat(),
                        'status': node_result.get('status'),
                        'duration_ms': duration_ms,
                        'error': node_result.get('error')
                    }
                    return merged

                return _wrapper

            # Add nodes
            for node in nodes_data:
                node_id = node['id']
                builder.add_node(node_id, make_node_wrapper(node_id))

            # Add linear edges
            node_ids = {n['id'] for n in nodes_data}
            for edge in edges_data:
                source = edge.get('source')
                target = edge.get('target')
                if source in node_ids and target in node_ids:
                    builder.add_edge(source, target)

            # Add conditional edges (optional)
            # Expected shape: {"source": "n1", "guards": [{"if": "content_type == 'image'", "target": "n2"}, ...]}
            def _make_route_fn(guards: List[Dict[str, Any]]):
                def _route(state: Dict[str, Any]) -> str:
                    # Very simple evaluator: supports equality of dotted keys to string/numeric literals
                    def _get_value(path: str):
                        parts = path.split('.')
                        val = state
                        for p in parts:
                            if isinstance(val, dict) and p in val:
                                val = val[p]
                            else:
                                return None
                        return val

                    for g in guards:
                        expr = (g.get('if') or '').strip()
                        tgt = g.get('target')
                        if not expr or not tgt:
                            continue
                        # Handle patterns like: key == 'value' or key == 123
                        if '==' in expr:
                            left, right = expr.split('==', 1)
                            left = left.strip()
                            right = right.strip().strip()  # keep quotes for now
                            left_val = _get_value(left)
                            # strip quotes if present
                            if (right.startswith("'") and right.endswith("'")) or (right.startswith('"') and right.endswith('"')):
                                right_val = right[1:-1]
                            else:
                                try:
                                    right_val = json.loads(right)
                                except Exception:
                                    right_val = right
                            if left_val == right_val:
                                return tgt
                    return '__end__'

                return _route

            for cond in conditions_data:
                source = cond.get('source')
                guards = cond.get('guards') or []
                if not source or not isinstance(guards, list):
                    continue
                targets = {g.get('target') for g in guards if g.get('target')}
                mapping: Dict[str, Any] = {t: t for t in targets if t}
                mapping['__end__'] = END
                builder.add_conditional_edges(source, _make_route_fn(guards), mapping)

            # Entry/exit points
            builder.set_entry_point(entry_node)
            # Always add END edge for safety from any node without outgoing edge
            # Here we conservatively add END from the last declared node
            if nodes_data:
                builder.add_edge(nodes_data[-1]['id'], END)

            return builder.compile(checkpointer=self.memory)
        except Exception as e:
            logger.error(f"Error building workflow: {e}", exc_info=True)
            return self._create_default_workflow()
    
    def execute_workflow(self, workflow_data: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow using a compiled LangGraph with wrapped nodes."""
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
            graph = self.build_workflow(workflow_data)
            # Provide required configurable keys for checkpointer
            checkpoint_ns = os.getenv('CHECKPOINT_NAMESPACE', 'workflows')
            config = {"configurable": {"thread_id": workflow_id, "checkpoint_ns": checkpoint_ns}}
            final_state = graph.invoke(initial_state, config=config)
            # Determine failures from executed nodes
            executed_nodes = final_state.get('nodes_executed', []) or []
            failed_nodes = [n for n in executed_nodes if (n or {}).get('status') == 'failed']
            has_failures = len(failed_nodes) > 0
            result = {
                'workflow_id': str(initial_state['workflow_id']),
                'start_time': str(initial_state['start_time']),
                'input_data': self._sanitize_for_json(input_data),
                'current_node': None,
                'status': 'failed' if has_failures else 'completed',
                'execution_id': str(initial_state['workflow_id']),
                'end_time': datetime.now().isoformat(),
                'failed_nodes': self._sanitize_for_json(failed_nodes) if has_failures else [],
                'error_details': [
                    {
                        'node_id': str(node.get('node_id', '')),
                        'error': str((node.get('result') or {}).get('error', 'Unknown error'))
                    }
                    for node in failed_nodes
                ] if has_failures else []
            }
            essential_keys = ['result', 'output', 'content', 'status', 'timestamp', 'image_url', 'social_data', 'instagram_post', 'node_results', 'nodes_executed']
            for key in essential_keys:
                if key in final_state:
                    value = final_state[key]
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

    def stream_execution(self, workflow_data: Dict[str, Any], input_data: Dict[str, Any]):
        """Yield step events during workflow execution for SSE consumers."""
        try:
            initial_state = {
                'workflow_id': str(uuid.uuid4()),
                'start_time': datetime.now().isoformat(),
                'input_data': input_data,
                'workflow_name': workflow_data.get('name', 'Unknown'),
                'nodes_executed': [],
                'node_results': {}
            }
            graph = self.build_workflow(workflow_data)
            # Provide required configurable keys for checkpointer
            checkpoint_ns = os.getenv('CHECKPOINT_NAMESPACE', 'workflows')
            config = {"configurable": {"thread_id": initial_state['workflow_id'], "checkpoint_ns": checkpoint_ns}}
            try:
                # Preferred: use LangGraph streaming API if available
                for event in graph.stream(initial_state, config=config):  # type: ignore[attr-defined]
                    # event is typically a (node_name, state) or dict depending on version
                    try:
                        import json as _json
                        if isinstance(event, tuple) and len(event) == 2:
                            node_name, state = event
                            payload = {
                                'type': 'node_event',
                                'node': node_name,
                                'timestamp': datetime.now().isoformat(),
                                'state_keys': list(state.keys()) if isinstance(state, dict) else []
                            }
                            yield f"data: {_json.dumps(payload)}\n\n"
                        elif isinstance(event, dict):
                            yield f"data: { _json.dumps(event) }\n\n"
                    except Exception:
                        continue
                # Final state after stream completes
                final_state = graph.invoke(initial_state, config=config)
                import json as _json
                yield f"data: {_json.dumps({'type': 'completed', 'execution_id': final_state.get('workflow_id')})}\n\n"
            except Exception:
                # Fallback: no native stream support; emit coarse events
                import time, json as _json
                yield f"data: {_json.dumps({'type': 'start', 'ts': datetime.now().isoformat()})}\n\n"
                # Execute non-streaming and emit summary
                result = self.execute_workflow(workflow_data, input_data)
                yield f"data: {_json.dumps({'type': 'completed', 'result': {'status': result.get('status'), 'execution_id': result.get('execution_id')}})}\n\n"
        except Exception as e:
            import json as _json
            yield f"data: {_json.dumps({'type': 'error', 'error': str(e)})}\n\n" 
