import asyncio
import time
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

from .node_executors.registry import executor_registry
from .node_executors.base import ExecutionContext, ExecutionResult

logger = logging.getLogger(__name__)

class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ExecutionStep:
    """Represents a single step in workflow execution"""
    node_id: str
    node_type: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    result: Optional[ExecutionResult] = None
    error: Optional[str] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowExecution:
    """Represents a workflow execution"""
    execution_id: str
    workflow_id: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    steps: List[ExecutionStep] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class WorkflowExecutor:
    """Main workflow execution engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.active_executions: Dict[str, WorkflowExecution] = {}
    
    async def execute_workflow(
        self, 
        workflow: Dict[str, Any], 
        inputs: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecution:
        """
        Execute a complete workflow
        
        Args:
            workflow: Workflow definition with nodes and edges
            inputs: Initial inputs for the workflow
            
        Returns:
            WorkflowExecution with results
        """
        execution_id = str(uuid.uuid4())
        workflow_id = workflow.get("id", "unknown")
        
        # Create execution context
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id
        )
        
        self.active_executions[execution_id] = execution
        
        try:
            self.logger.info(f"Starting workflow execution: {execution_id}")
            execution.status = ExecutionStatus.RUNNING
            execution.start_time = time.time()
            
            # Initialize execution steps
            nodes = workflow.get("nodes", [])
            edges = workflow.get("edges", [])
            
            # Create execution steps
            execution.steps = [
                ExecutionStep(
                    node_id=node["id"],
                    node_type=node["type"],
                    inputs={}
                )
                for node in nodes
            ]
            
            # Build node dependency graph
            node_dependencies = self._build_dependency_graph(nodes, edges)
            
            # Execute nodes in dependency order
            await self._execute_nodes(execution, nodes, node_dependencies, inputs or {})
            
            execution.status = ExecutionStatus.COMPLETED
            execution.end_time = time.time()
            
            self.logger.info(f"Workflow execution completed: {execution_id}")
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {execution_id}", exc_info=True)
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)
            execution.end_time = time.time()
        
        finally:
            # Clean up
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
        
        return execution
    
    def _build_dependency_graph(
        self, 
        nodes: List[Dict[str, Any]], 
        edges: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Build dependency graph for nodes"""
        dependencies = {node["id"]: [] for node in nodes}
        
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            if source and target:
                if target not in dependencies:
                    dependencies[target] = []
                dependencies[target].append(source)
        
        return dependencies
    
    async def _execute_nodes(
        self,
        execution: WorkflowExecution,
        nodes: List[Dict[str, Any]],
        dependencies: Dict[str, List[str]],
        initial_inputs: Dict[str, Any]
    ):
        """Execute nodes in dependency order"""
        node_results = {}
        node_outputs = {}
        
        # Add initial inputs to node outputs
        node_outputs.update(initial_inputs)
        
        # Execute nodes in topological order
        executed_nodes = set()
        
        while len(executed_nodes) < len(nodes):
            # Find nodes ready to execute
            ready_nodes = []
            for node in nodes:
                node_id = node["id"]
                if node_id in executed_nodes:
                    continue
                
                # Check if all dependencies are satisfied
                node_deps = dependencies.get(node_id, [])
                if all(dep in executed_nodes for dep in node_deps):
                    ready_nodes.append(node)
            
            if not ready_nodes:
                # Check for circular dependencies
                remaining = [node["id"] for node in nodes if node["id"] not in executed_nodes]
                raise Exception(f"Circular dependency detected. Remaining nodes: {remaining}")
            
            # Execute ready nodes in parallel
            tasks = []
            for node in ready_nodes:
                task = self._execute_single_node(
                    execution, node, node_outputs, node_results
                )
                tasks.append(task)
            
            # Wait for all ready nodes to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Node execution failed: {result}")
                    raise result
                
                node_id = ready_nodes[i]["id"]
                executed_nodes.add(node_id)
                
                # Store results
                if result.success:
                    node_results[node_id] = result
                    node_outputs[node_id] = result.output
                else:
                    raise Exception(f"Node {node_id} failed: {result.error}")
    
    async def _execute_single_node(
        self,
        execution: WorkflowExecution,
        node: Dict[str, Any],
        node_outputs: Dict[str, Any],
        node_results: Dict[str, ExecutionResult]
    ) -> ExecutionResult:
        """Execute a single node"""
        node_id = node["id"]
        node_type = node["type"]
        
        # Find execution step
        step = next((s for s in execution.steps if s.node_id == node_id), None)
        if not step:
            raise Exception(f"Execution step not found for node: {node_id}")
        
        step.status = ExecutionStatus.RUNNING
        step.start_time = time.time()
        
        try:
            self.logger.info(f"Executing node: {node_id} ({node_type})")
            
            # Get executor
            executor = executor_registry.get_executor(node_type)
            if not executor:
                raise Exception(f"No executor found for node type: {node_type}")
            
            # Prepare inputs
            inputs = self._prepare_node_inputs(node, node_outputs)
            step.inputs = inputs
            
            # Create execution context
            context = ExecutionContext(
                workflow_id=execution.workflow_id,
                execution_id=execution.execution_id,
                node_id=node_id,
                inputs=inputs,
                config=node.get("data", {}).get("config", {}),
                previous_outputs=node_outputs
            )
            
            # Execute node
            result = await executor.execute(context)
            step.result = result
            step.outputs = result.output if result.success else {}
            
            if result.success:
                step.status = ExecutionStatus.COMPLETED
                self.logger.info(f"Node completed successfully: {node_id}")
            else:
                step.status = ExecutionStatus.FAILED
                step.error = result.error
                self.logger.error(f"Node failed: {node_id} - {result.error}")
            
            step.end_time = time.time()
            return result
            
        except Exception as e:
            step.status = ExecutionStatus.FAILED
            step.error = str(e)
            step.end_time = time.time()
            self.logger.error(f"Node execution error: {node_id}", exc_info=True)
            raise
    
    def _prepare_node_inputs(
        self, 
        node: Dict[str, Any], 
        node_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare inputs for a node based on previous outputs"""
        inputs = {}
        
        # Get input configuration from node
        node_data = node.get("data", {})
        input_config = node_data.get("inputs", {})
        
        for input_key, input_spec in input_config.items():
            if isinstance(input_spec, str):
                # Direct reference to another node's output
                if input_spec in node_outputs:
                    inputs[input_key] = node_outputs[input_spec]
            elif isinstance(input_spec, dict):
                # Complex input specification
                source_node = input_spec.get("source")
                source_field = input_spec.get("field", "data")
                
                if source_node and source_node in node_outputs:
                    source_output = node_outputs[source_node]
                    if isinstance(source_output, dict) and source_field in source_output:
                        inputs[input_key] = source_output[source_field]
                    else:
                        inputs[input_key] = source_output
        
        return inputs
    
    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get status of an execution"""
        return self.active_executions.get(execution_id)
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel an active execution"""
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            execution.status = ExecutionStatus.CANCELLED
            execution.end_time = time.time()
            return True
        return False
    
    def list_active_executions(self) -> List[str]:
        """List all active execution IDs"""
        return list(self.active_executions.keys())

# Global workflow executor instance
workflow_executor = WorkflowExecutor()
