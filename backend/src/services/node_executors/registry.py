from typing import Dict, Type, Optional, List, Any
import logging
from .base import BaseNodeExecutor

logger = logging.getLogger(__name__)

class NodeExecutorRegistry:
    """Registry for managing node executors"""
    
    def __init__(self):
        self._executors: Dict[str, Type[BaseNodeExecutor]] = {}
        self._instances: Dict[str, BaseNodeExecutor] = {}
    
    def register(self, node_type: str, executor_class: Type[BaseNodeExecutor]) -> None:
        """
        Register a node executor class
        
        Args:
            node_type: The node type this executor handles
            executor_class: The executor class to register
        """
        if not issubclass(executor_class, BaseNodeExecutor):
            raise ValueError(f"Executor class must inherit from BaseNodeExecutor")
        
        self._executors[node_type] = executor_class
        logger.info(f"Registered executor for node type: {node_type}")
    
    def get_executor(self, node_type: str) -> Optional[BaseNodeExecutor]:
        """
        Get an executor instance for the given node type
        
        Args:
            node_type: The node type to get executor for
            
        Returns:
            Executor instance or None if not found
        """
        if node_type not in self._executors:
            logger.warning(f"No executor registered for node type: {node_type}")
            return None
        
        # Create instance if not already cached
        if node_type not in self._instances:
            executor_class = self._executors[node_type]
            self._instances[node_type] = executor_class(node_type)
        
        return self._instances[node_type]
    
    def get_executor_class(self, node_type: str) -> Optional[Type[BaseNodeExecutor]]:
        """
        Get the executor class for the given node type
        
        Args:
            node_type: The node type to get executor class for
            
        Returns:
            Executor class or None if not found
        """
        return self._executors.get(node_type)
    
    def list_available_types(self) -> List[str]:
        """
        Get list of all registered node types
        
        Returns:
            List of registered node type names
        """
        return list(self._executors.keys())
    
    def is_supported(self, node_type: str) -> bool:
        """
        Check if a node type is supported
        
        Args:
            node_type: The node type to check
            
        Returns:
            True if supported, False otherwise
        """
        return node_type in self._executors
    
    def get_executor_info(self, node_type: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an executor
        
        Args:
            node_type: The node type to get info for
            
        Returns:
            Dictionary with executor information or None if not found
        """
        executor = self.get_executor(node_type)
        if not executor:
            return None
        
        return {
            "node_type": node_type,
            "class_name": executor.__class__.__name__,
            "required_inputs": executor.get_required_inputs(),
            "optional_inputs": executor.get_optional_inputs(),
            "output_schema": executor.get_output_schema(),
            "description": getattr(executor, '__doc__', 'No description available')
        }
    
    def clear_cache(self) -> None:
        """Clear the executor instance cache"""
        self._instances.clear()
        logger.info("Cleared executor instance cache")

# Global registry instance
executor_registry = NodeExecutorRegistry()
