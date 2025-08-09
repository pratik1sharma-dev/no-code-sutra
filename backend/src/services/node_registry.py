"""
Centralized Node Registry for No Code Sutra
Single source of truth for all node types and their metadata
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class NodeCategory(Enum):
    AI_ML = "AI & ML"
    COMMUNICATION = "Communication"
    DATA = "Data"
    SOCIAL_MEDIA = "Social Media"
    CONTROL_FLOW = "Control Flow"
    INTEGRATION = "Integration"

@dataclass
class NodeMetadata:
    type: str
    label: str
    description: str
    category: NodeCategory
    icon: str  # Frontend icon name
    color: str
    required_inputs: List[str]
    optional_inputs: List[str]
    output_schema: Dict[str, Any]
    is_active: bool = True

class NodeRegistry:
    """Centralized registry for all node types"""
    
    def __init__(self):
        self._nodes: Dict[str, NodeMetadata] = {}
        self._initialize_default_nodes()
    
    def _initialize_default_nodes(self):
        """Initialize all available node types"""
        
        # AI & ML Nodes
        self._nodes['aiAgent'] = NodeMetadata(
            type='aiAgent',
            label='AI Agent',
            description='AI-powered tasks (research, analysis, content generation)',
            category=NodeCategory.AI_ML,
            icon='Bot',
            color='primary',
            required_inputs=['task', 'prompt'],
            optional_inputs=['model', 'temperature', 'max_tokens'],
            output_schema={'type': 'object', 'properties': {'result': {'type': 'string'}}}
        )
        
        # Social Media Nodes
        self._nodes['instagram_post'] = NodeMetadata(
            type='instagram_post',
            label='Instagram Post',
            description='Post content to Instagram Business accounts',
            category=NodeCategory.SOCIAL_MEDIA,
            icon='Instagram',
            color='pink',
            required_inputs=['content', 'instagram_credentials'],
            optional_inputs=['scheduled_time', 'location', 'user_tags'],
            output_schema={'type': 'object', 'properties': {'post_id': {'type': 'string'}}}
        )
        
        # Communication Nodes
        self._nodes['email'] = NodeMetadata(
            type='email',
            label='Email',
            description='Send automated emails with templates',
            category=NodeCategory.COMMUNICATION,
            icon='Mail',
            color='success',
            required_inputs=['to', 'subject', 'template'],
            optional_inputs=['variables', 'attachments'],
            output_schema={'type': 'object', 'properties': {'message_id': {'type': 'string'}}}
        )
        
        self._nodes['slack'] = NodeMetadata(
            type='slack',
            label='Slack',
            description='Send messages to Slack channels',
            category=NodeCategory.COMMUNICATION,
            icon='MessageSquare',
            color='primary',
            required_inputs=['channel', 'message'],
            optional_inputs=['attachments', 'thread_ts'],
            output_schema={'type': 'object', 'properties': {'ts': {'type': 'string'}}}
        )
        
        # Data Nodes
        self._nodes['webScraper'] = NodeMetadata(
            type='webScraper',
            label='Web Scraper',
            description='Extract data from websites and web pages',
            category=NodeCategory.DATA,
            icon='Globe',
            color='secondary',
            required_inputs=['url', 'selectors'],
            optional_inputs=['headers', 'timeout'],
            output_schema={'type': 'object', 'properties': {'data': {'type': 'array'}}}
        )
        
        self._nodes['data'] = NodeMetadata(
            type='data',
            label='Data',
            description='Data processing, storage, and manipulation',
            category=NodeCategory.DATA,
            icon='Database',
            color='secondary',
            required_inputs=['operation'],
            optional_inputs=['source', 'filters', 'transformations'],
            output_schema={'type': 'object', 'properties': {'result': {'type': 'any'}}}
        )
        
        # Control Flow Nodes
        self._nodes['condition'] = NodeMetadata(
            type='condition',
            label='Condition',
            description='Conditional logic and branching',
            category=NodeCategory.CONTROL_FLOW,
            icon='GitBranch',
            color='warning',
            required_inputs=['condition'],
            optional_inputs=['true_path', 'false_path'],
            output_schema={'type': 'object', 'properties': {'result': {'type': 'boolean'}}}
        )
        
        self._nodes['delay'] = NodeMetadata(
            type='delay',
            label='Delay',
            description='Time delays and scheduling',
            category=NodeCategory.CONTROL_FLOW,
            icon='Clock',
            color='secondary',
            required_inputs=['duration'],
            optional_inputs=['unit'],
            output_schema={'type': 'object', 'properties': {'completed': {'type': 'boolean'}}}
        )
        
        # Integration Nodes
        self._nodes['apiCall'] = NodeMetadata(
            type='apiCall',
            label='API Call',
            description='External API integrations (social media, third-party services)',
            category=NodeCategory.INTEGRATION,
            icon='Globe',
            color='primary',
            required_inputs=['url', 'method'],
            optional_inputs=['headers', 'body', 'auth'],
            output_schema={'type': 'object', 'properties': {'response': {'type': 'any'}}}
        )
        
        # Additional nodes...
        self._nodes['notification'] = NodeMetadata(
            type='notification',
            label='Notification',
            description='Send notifications (push, SMS, in-app)',
            category=NodeCategory.COMMUNICATION,
            icon='Bell',
            color='warning',
            required_inputs=['message', 'type'],
            optional_inputs=['recipients', 'priority'],
            output_schema={'type': 'object', 'properties': {'sent': {'type': 'boolean'}}}
        )
        
        self._nodes['fileOperation'] = NodeMetadata(
            type='fileOperation',
            label='File Operation',
            description='File operations (read, write, move, delete)',
            category=NodeCategory.DATA,
            icon='FolderOpen',
            color='secondary',
            required_inputs=['operation', 'path'],
            optional_inputs=['content', 'destination'],
            output_schema={'type': 'object', 'properties': {'success': {'type': 'boolean'}}}
        )
        
        self._nodes['database'] = NodeMetadata(
            type='database',
            label='Database',
            description='Database operations (query, insert, update, delete)',
            category=NodeCategory.DATA,
            icon='Server',
            color='secondary',
            required_inputs=['operation', 'query'],
            optional_inputs=['connection', 'parameters'],
            output_schema={'type': 'object', 'properties': {'result': {'type': 'any'}}}
        )
        
        self._nodes['schedule'] = NodeMetadata(
            type='schedule',
            label='Schedule',
            description='Recurring task scheduling',
            category=NodeCategory.CONTROL_FLOW,
            icon='Calendar',
            color='secondary',
            required_inputs=['cron'],
            optional_inputs=['timezone', 'enabled'],
            output_schema={'type': 'object', 'properties': {'scheduled': {'type': 'boolean'}}}
        )
        
        self._nodes['transform'] = NodeMetadata(
            type='transform',
            label='Transform',
            description='Data transformation (CSV↔JSON, format conversion)',
            category=NodeCategory.DATA,
            icon='Zap',
            color='secondary',
            required_inputs=['input', 'transformation'],
            optional_inputs=['options'],
            output_schema={'type': 'object', 'properties': {'output': {'type': 'any'}}}
        )
        
        self._nodes['filter'] = NodeMetadata(
            type='filter',
            label='Filter',
            description='Data filtering based on conditions',
            category=NodeCategory.DATA,
            icon='Filter',
            color='secondary',
            required_inputs=['data', 'condition'],
            optional_inputs=['options'],
            output_schema={'type': 'object', 'properties': {'filtered_data': {'type': 'array'}}}
        )
        
        self._nodes['aggregate'] = NodeMetadata(
            type='aggregate',
            label='Aggregate',
            description='Data aggregation (group, sum, count, average)',
            category=NodeCategory.DATA,
            icon='BarChart3',
            color='secondary',
            required_inputs=['data', 'operation'],
            optional_inputs=['group_by', 'filters'],
            output_schema={'type': 'object', 'properties': {'result': {'type': 'any'}}}
        )
        
        self._nodes['errorHandler'] = NodeMetadata(
            type='errorHandler',
            label='Error Handler',
            description='Error handling and recovery',
            category=NodeCategory.CONTROL_FLOW,
            icon='AlertTriangle',
            color='error',
            required_inputs=['error_type'],
            optional_inputs=['fallback_action', 'retry_count'],
            output_schema={'type': 'object', 'properties': {'handled': {'type': 'boolean'}}}
        )
    
    def get_node_metadata(self, node_type: str) -> Optional[NodeMetadata]:
        """Get metadata for a specific node type"""
        return self._nodes.get(node_type)
    
    def get_all_node_types(self) -> List[str]:
        """Get all available node types"""
        return list(self._nodes.keys())
    
    def get_active_node_types(self) -> List[str]:
        """Get only active node types"""
        return [node_type for node_type, metadata in self._nodes.items() if metadata.is_active]
    
    def get_nodes_by_category(self, category: NodeCategory) -> List[str]:
        """Get node types by category"""
        return [node_type for node_type, metadata in self._nodes.items() if metadata.category == category]
    
    def is_valid_node_type(self, node_type: str) -> bool:
        """Check if a node type is valid and active"""
        metadata = self._nodes.get(node_type)
        return metadata is not None and metadata.is_active
    
    def get_node_count(self) -> int:
        """Get total number of available node types"""
        return len(self._nodes)
    
    def get_frontend_config(self) -> Dict[str, Any]:
        """Get node configuration for frontend consumption"""
        config = {}
        for node_type, metadata in self._nodes.items():
            if metadata.is_active:
                config[node_type] = {
                    'type': metadata.type,
                    'label': metadata.label,
                    'description': metadata.description,
                    'icon': metadata.icon,
                    'color': metadata.color,
                    'category': metadata.category.value,
                    'required_inputs': metadata.required_inputs,
                    'optional_inputs': metadata.optional_inputs
                }
        return config

# Global instance
node_registry = NodeRegistry()
