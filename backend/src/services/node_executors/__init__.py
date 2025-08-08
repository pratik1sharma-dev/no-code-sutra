# Node Executors Package

from .base import BaseNodeExecutor, ExecutionContext, ExecutionResult, NodeStatus
from .registry import executor_registry, NodeExecutorRegistry
from .data_executor import DataNodeExecutor

# Register available executors
def register_executors():
    """Register all available node executors"""
    executor_registry.register("data", DataNodeExecutor)
    
    # TODO: Register other executors as they are implemented
    # executor_registry.register("aiAgent", AIAgentExecutor)
    # executor_registry.register("webScraper", WebScraperExecutor)
    # executor_registry.register("email", EmailExecutor)
    # executor_registry.register("slack", SlackExecutor)
    # executor_registry.register("notification", NotificationExecutor)
    # executor_registry.register("fileOperation", FileOperationExecutor)
    # executor_registry.register("database", DatabaseExecutor)
    # executor_registry.register("apiCall", APICallExecutor)
    # executor_registry.register("condition", ConditionExecutor)
    # executor_registry.register("delay", DelayExecutor)
    # executor_registry.register("schedule", ScheduleExecutor)
    # executor_registry.register("transform", TransformExecutor)
    # executor_registry.register("filter", FilterExecutor)
    # executor_registry.register("aggregate", AggregateExecutor)
    # executor_registry.register("errorHandler", ErrorHandlerExecutor)

# Auto-register executors when module is imported
register_executors()

__all__ = [
    "BaseNodeExecutor",
    "ExecutionContext", 
    "ExecutionResult",
    "NodeStatus",
    "executor_registry",
    "NodeExecutorRegistry",
    "DataNodeExecutor",
    "register_executors"
]
