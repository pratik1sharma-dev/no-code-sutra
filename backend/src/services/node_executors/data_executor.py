import time
import json
from typing import Dict, Any, List, Optional
from .base import BaseNodeExecutor, ExecutionContext, ExecutionResult

class DataNodeExecutor(BaseNodeExecutor):
    """
    Executor for data processing and manipulation nodes
    
    Supports operations like:
    - Data extraction and mapping
    - Data validation
    - Data transformation
    - Data storage and retrieval
    """
    
    def __init__(self, node_type: str = "data"):
        super().__init__(node_type)
    
    async def execute(self, context: ExecutionContext) -> ExecutionResult:
        """Execute data processing logic"""
        start_time = time.time()
        
        try:
            # Pre-execution validation
            if not await self.pre_execute(context):
                return ExecutionResult(
                    success=False,
                    output=None,
                    error="Pre-execution validation failed"
                )
            
            # Get operation type from config
            operation = context.config.get("operation", "pass_through")
            
            # Execute based on operation type
            if operation == "pass_through":
                result = await self._pass_through(context)
            elif operation == "extract":
                result = await self._extract_data(context)
            elif operation == "map":
                result = await self._map_data(context)
            elif operation == "validate":
                result = await self._validate_data(context)
            elif operation == "transform":
                result = await self._transform_data(context)
            elif operation == "store":
                result = await self._store_data(context)
            else:
                return ExecutionResult(
                    success=False,
                    output=None,
                    error=f"Unknown operation: {operation}"
                )
            
            execution_time = time.time() - start_time
            
            # Post-execution processing
            result.execution_time = execution_time
            return await self.post_execute(result, context)
            
        except Exception as e:
            self.logger.error(f"Error executing data node: {e}", exc_info=True)
            return ExecutionResult(
                success=False,
                output=None,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate data node configuration"""
        errors = []
        
        operation = config.get("operation")
        if operation and operation not in ["pass_through", "extract", "map", "validate", "transform", "store"]:
            errors.append(f"Invalid operation: {operation}")
        
        # Validate operation-specific config
        if operation == "extract":
            if "fields" not in config:
                errors.append("extract operation requires 'fields' configuration")
        
        elif operation == "map":
            if "mapping" not in config:
                errors.append("map operation requires 'mapping' configuration")
        
        elif operation == "validate":
            if "rules" not in config:
                errors.append("validate operation requires 'rules' configuration")
        
        elif operation == "transform":
            if "transformation" not in config:
                errors.append("transform operation requires 'transformation' configuration")
        
        elif operation == "store":
            if "storage_type" not in config:
                errors.append("store operation requires 'storage_type' configuration")
        
        return errors
    
    def get_required_inputs(self) -> List[str]:
        """Get required inputs for data node"""
        return ["data"]
    
    def get_optional_inputs(self) -> List[str]:
        """Get optional inputs for data node"""
        return ["metadata", "schema"]
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get output schema for data node"""
        return {
            "type": "object",
            "description": "Processed data output",
            "properties": {
                "data": {"type": "any", "description": "Processed data"},
                "metadata": {"type": "object", "description": "Processing metadata"},
                "validation_results": {"type": "array", "description": "Validation results if applicable"}
            }
        }
    
    async def _pass_through(self, context: ExecutionContext) -> ExecutionResult:
        """Pass data through without modification"""
        return ExecutionResult(
            success=True,
            output={
                "data": context.inputs.get("data"),
                "metadata": {"operation": "pass_through"}
            }
        )
    
    async def _extract_data(self, context: ExecutionContext) -> ExecutionResult:
        """Extract specific fields from data"""
        data = context.inputs.get("data", {})
        fields = context.config.get("fields", [])
        
        if isinstance(data, dict):
            extracted = {field: data.get(field) for field in fields}
        elif isinstance(data, list):
            extracted = [{field: item.get(field) for field in fields} for item in data]
        else:
            return ExecutionResult(
                success=False,
                output=None,
                error="Data must be dict or list for extract operation"
            )
        
        return ExecutionResult(
            success=True,
            output={
                "data": extracted,
                "metadata": {"operation": "extract", "fields": fields}
            }
        )
    
    async def _map_data(self, context: ExecutionContext) -> ExecutionResult:
        """Map data using specified mapping rules"""
        data = context.inputs.get("data", {})
        mapping = context.config.get("mapping", {})
        
        if isinstance(data, dict):
            mapped = {}
            for old_key, new_key in mapping.items():
                if old_key in data:
                    mapped[new_key] = data[old_key]
        elif isinstance(data, list):
            mapped = []
            for item in data:
                mapped_item = {}
                for old_key, new_key in mapping.items():
                    if old_key in item:
                        mapped_item[new_key] = item[old_key]
                mapped.append(mapped_item)
        else:
            return ExecutionResult(
                success=False,
                output=None,
                error="Data must be dict or list for map operation"
            )
        
        return ExecutionResult(
            success=True,
            output={
                "data": mapped,
                "metadata": {"operation": "map", "mapping": mapping}
            }
        )
    
    async def _validate_data(self, context: ExecutionContext) -> ExecutionResult:
        """Validate data against rules"""
        data = context.inputs.get("data")
        rules = context.config.get("rules", [])
        
        validation_results = []
        is_valid = True
        
        for rule in rules:
            rule_type = rule.get("type")
            field = rule.get("field")
            value = rule.get("value")
            
            if rule_type == "required":
                if field not in data or data[field] is None:
                    validation_results.append({
                        "rule": rule,
                        "valid": False,
                        "message": f"Required field '{field}' is missing or null"
                    })
                    is_valid = False
                else:
                    validation_results.append({
                        "rule": rule,
                        "valid": True,
                        "message": f"Field '{field}' is present"
                    })
            
            elif rule_type == "type":
                if field in data:
                    expected_type = value
                    actual_type = type(data[field]).__name__
                    if actual_type != expected_type:
                        validation_results.append({
                            "rule": rule,
                            "valid": False,
                            "message": f"Field '{field}' should be {expected_type}, got {actual_type}"
                        })
                        is_valid = False
                    else:
                        validation_results.append({
                            "rule": rule,
                            "valid": True,
                            "message": f"Field '{field}' has correct type {expected_type}"
                        })
        
        return ExecutionResult(
            success=is_valid,
            output={
                "data": data,
                "metadata": {"operation": "validate"},
                "validation_results": validation_results
            },
            error=None if is_valid else "Data validation failed"
        )
    
    async def _transform_data(self, context: ExecutionContext) -> ExecutionResult:
        """Transform data using specified transformation"""
        data = context.inputs.get("data")
        transformation = context.config.get("transformation", {})
        
        # Simple transformation examples
        if transformation.get("uppercase"):
            if isinstance(data, str):
                transformed = data.upper()
            elif isinstance(data, dict):
                transformed = {k: v.upper() if isinstance(v, str) else v for k, v in data.items()}
            else:
                transformed = data
        elif transformation.get("lowercase"):
            if isinstance(data, str):
                transformed = data.lower()
            elif isinstance(data, dict):
                transformed = {k: v.lower() if isinstance(v, str) else v for k, v in data.items()}
            else:
                transformed = data
        else:
            transformed = data
        
        return ExecutionResult(
            success=True,
            output={
                "data": transformed,
                "metadata": {"operation": "transform", "transformation": transformation}
            }
        )
    
    async def _store_data(self, context: ExecutionContext) -> ExecutionResult:
        """Store data (placeholder implementation)"""
        data = context.inputs.get("data")
        storage_type = context.config.get("storage_type", "memory")
        
        # For now, just return success (actual storage would be implemented later)
        return ExecutionResult(
            success=True,
            output={
                "data": data,
                "metadata": {"operation": "store", "storage_type": storage_type, "stored": True}
            }
        )
