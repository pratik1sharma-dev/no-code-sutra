"""
Data Mapping Utility for No Code Sutra Workflows
Handles data flow between nodes in workflow execution
"""

import json
from typing import Dict, Any, Optional

class DataMapper:
    """Handles data mapping between workflow nodes"""
    
    @staticmethod
    def map_data_for_node(node_type: str, source_outputs: Dict[str, Any], edge_mapping: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Map data from source nodes to target node based on node type and edge mapping
        
        Args:
            node_type: Type of target node (aiAgent, textOverlay, instagram_post, etc.)
            source_outputs: Dictionary of outputs from source nodes
            edge_mapping: Optional mapping configuration from edge
            
        Returns:
            Mapped input data for the target node
        """
        
        if node_type == 'aiAgent':
            # AI Agent doesn't need input mapping - it uses its own config
            return {}
            
        elif node_type == 'textOverlay':
            return DataMapper._map_for_text_overlay(source_outputs, edge_mapping)
            
        elif node_type == 'imageUpload':
            return DataMapper._map_for_image_upload(source_outputs, edge_mapping)
            
        elif node_type == 'instagram_post':
            return DataMapper._map_for_instagram_post(source_outputs, edge_mapping)
            
        elif node_type == 'email':
            return DataMapper._map_for_email(source_outputs, edge_mapping)
            
        elif node_type == 'slack':
            return DataMapper._map_for_slack(source_outputs, edge_mapping)
            
        else:
            # Default mapping - pass through all outputs
            return source_outputs
    
    @staticmethod
    def _map_for_text_overlay(source_outputs: Dict[str, Any], edge_mapping: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Map data for Text Overlay node"""
        mapped_data = {}
        
        # Look for AI Agent output
        for source_id, output in source_outputs.items():
            if isinstance(output, dict):
                # If it's structured JSON from AI Agent
                if 'headline' in output and 'bullets' in output:
                    mapped_data['ai_output'] = output
                    break
                # If it's the old format with 'result' field
                elif 'result' in output:
                    try:
                        # Try to parse the result as JSON
                        parsed_result = json.loads(output['result'])
                        mapped_data['ai_output'] = parsed_result
                    except (json.JSONDecodeError, TypeError):
                        # If it's not JSON, use as-is
                        mapped_data['ai_output'] = output
                    break
        
        # Apply edge mapping if provided
        if edge_mapping:
            for target_field, source_path in edge_mapping.items():
                if source_path in source_outputs:
                    mapped_data[target_field] = source_outputs[source_path]
        
        return mapped_data
    
    @staticmethod
    def _map_for_image_upload(source_outputs: Dict[str, Any], edge_mapping: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Map data for Image Upload node"""
        mapped_data = {}
        
        # Look for image URL from Text Overlay
        for source_id, output in source_outputs.items():
            if isinstance(output, dict) and 'image_url' in output:
                mapped_data['image_data_url'] = output['image_url']
                break
        
        # Apply edge mapping if provided
        if edge_mapping:
            for target_field, source_path in edge_mapping.items():
                if source_path in source_outputs:
                    mapped_data[target_field] = source_outputs[source_path]
        
        return mapped_data
    
    @staticmethod
    def _map_for_instagram_post(source_outputs: Dict[str, Any], edge_mapping: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Map data for Instagram Post node"""
        mapped_data = {}
        
        # Look for AI Agent output (caption, hashtags) and image URL
        for source_id, output in source_outputs.items():
            if isinstance(output, dict):
                # AI Agent output with caption and hashtags
                if 'caption' in output and 'hashtags' in output:
                    mapped_data['ai_output'] = output
                # Image URL from Image Upload
                elif 'image_url' in output:
                    mapped_data['image_url'] = output['image_url']
        
        # Apply edge mapping if provided
        if edge_mapping:
            for target_field, source_path in edge_mapping.items():
                if source_path in source_outputs:
                    mapped_data[target_field] = source_outputs[source_path]
        
        return mapped_data
    
    @staticmethod
    def _map_for_email(source_outputs: Dict[str, Any], edge_mapping: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Map data for Email node"""
        mapped_data = {}
        
        # Look for AI Agent output with email content
        for source_id, output in source_outputs.items():
            if isinstance(output, dict):
                if 'subject' in output and 'body' in output:
                    mapped_data['ai_output'] = output
                    break
        
        # Apply edge mapping if provided
        if edge_mapping:
            for target_field, source_path in edge_mapping.items():
                if source_path in source_outputs:
                    mapped_data[target_field] = source_outputs[source_path]
        
        return mapped_data
    
    @staticmethod
    def _map_for_slack(source_outputs: Dict[str, Any], edge_mapping: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Map data for Slack node"""
        mapped_data = {}
        
        # Look for AI Agent output with message content
        for source_id, output in source_outputs.items():
            if isinstance(output, dict):
                if 'message' in output or 'content' in output:
                    mapped_data['ai_output'] = output
                    break
        
        # Apply edge mapping if provided
        if edge_mapping:
            for target_field, source_path in edge_mapping.items():
                if source_path in source_outputs:
                    mapped_data[target_field] = source_outputs[source_path]
        
        return mapped_data
    
    @staticmethod
    def extract_field_from_output(output: Any, field_path: str) -> Any:
        """
        Extract a specific field from node output using dot notation
        
        Args:
            output: Node output data
            field_path: Path to field (e.g., 'ai_agent_1.output.headline')
            
        Returns:
            Extracted field value
        """
        try:
            parts = field_path.split('.')
            current = output
            
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
            
            return current
        except (KeyError, TypeError, AttributeError):
            return None
