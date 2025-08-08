from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class NodeStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"

@dataclass
class ExecutionContext:
    """Context passed to node executors during workflow execution"""
    workflow_id: str
    execution_id: str
    node_id: str
    inputs: Dict[str, Any]
    config: Dict[str, Any]
    previous_outputs: Dict[str, Any] = None
    global_variables: Dict[str, Any] = None

@dataclass
class ExecutionResult:
    """Result returned by node executors"""
    success: bool
    output: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None

class BaseNodeExecutor(ABC):
    """Abstract base class for all node executors"""
    
    def __init__(self, node_type: str):
        self.node_type = node_type
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        """
        Execute the node logic
        
        Args:
            context: Execution context containing inputs, config, etc.
            
        Returns:
            ExecutionResult with success status, output, and metadata
        """
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate node configuration
        
        Args:
            config: Node configuration dictionary
            
        Returns:
            List of validation error messages (empty if valid)
        """
        return []
    
    def get_required_inputs(self) -> List[str]:
        """
        Get list of required input keys for this node type
        
        Returns:
            List of required input key names
        """
        return []
    
    def get_optional_inputs(self) -> List[str]:
        """
        Get list of optional input keys for this node type
        
        Returns:
            List of optional input key names
        """
        return []
    
    def get_output_schema(self) -> Dict[str, Any]:
        """
        Get the output schema for this node type
        
        Returns:
            Dictionary describing the output structure
        """
        return {"type": "any", "description": "Node output"}
    
    async def pre_execute(self, context: ExecutionContext) -> bool:
        """
        Pre-execution validation and setup
        
        Args:
            context: Execution context
            
        Returns:
            True if pre-execution checks pass, False otherwise
        """
        # Validate configuration
        config_errors = self.validate_config(context.config)
        if config_errors:
            self.logger.error(f"Configuration validation failed: {config_errors}")
            return False
        
        # Validate required inputs
        required_inputs = self.get_required_inputs()
        missing_inputs = [input_key for input_key in required_inputs 
                         if input_key not in context.inputs]
        if missing_inputs:
            self.logger.error(f"Missing required inputs: {missing_inputs}")
            return False
        
        return True
    
    async def post_execute(self, result: ExecutionResult, context: ExecutionContext) -> ExecutionResult:
        """
        Post-execution processing and cleanup
        
        Args:
            result: Execution result
            context: Execution context
            
        Returns:
            Potentially modified execution result
        """
        return result
    
    def __str__(self):
        return f"{self.__class__.__name__}(type={self.node_type})"
