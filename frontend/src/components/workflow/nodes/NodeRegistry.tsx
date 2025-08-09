import React, { useEffect, useState } from 'react';
import type { NodeProps } from 'reactflow';
import { 
  Bot, 
  Mail, 
  MessageSquare, 
  Database, 
  GitBranch, 
  Clock, 
  Calendar,
  FileText,
  Share2,
  Image,
  Search,
  Brain,
  Globe,
  Bell,
  FolderOpen,
  Server,
  Zap,
  Filter,
  BarChart3,
  AlertTriangle,
  Instagram
} from 'lucide-react';
import type { WorkflowNodeData, NodeType } from '../../../types/workflow';
import { BaseNode } from './BaseNode';
import { AIAgentNode } from './AIAgentNode';
import { EmailNode } from './EmailNode';
import { InstagramPostNode } from './InstagramPostNode';
import { nodeRegistryService } from '../../../services/nodeRegistryService';
import type { NodeMetadata } from '../../../services/nodeRegistryService';

// Icon mapping for dynamic loading
const ICON_MAP: Record<string, React.ComponentType<any>> = {
  Bot,
  Globe,
  Mail,
  MessageSquare,
  Bell,
  Database,
  FolderOpen,
  Server,
  Instagram,
  GitBranch,
  Clock,
  Calendar,
  Zap,
  Filter,
  BarChart3,
  AlertTriangle,
  Search,
  Brain,
  FileText,
  Share2,
  Image
};

// Dynamic node types - populated from backend registry
export const NODE_TYPES: Record<string, any> = {};

// Default node component for unimplemented nodes
const DefaultNode: React.FC<NodeProps<WorkflowNodeData>> = (props) => {
  const { data } = props;
  const nodeType = NODE_TYPES[data.type];
  const Icon = nodeType?.icon ? ICON_MAP[nodeType.icon] || Bot : Bot;

  return (
    <BaseNode
      {...props}
      icon={<Icon className="w-4 h-4" />}
      color={nodeType?.color || 'primary'}
    >
      <div className="text-xs text-gray-500">
        {nodeType?.description || 'Node type not implemented yet'}
      </div>
    </BaseNode>
  );
};

// Placeholder components for unimplemented nodes
const WebScraperNode = DefaultNode;
const SlackNode = DefaultNode;
const NotificationNode = DefaultNode;
const DataNode = DefaultNode;
const FileOperationNode = DefaultNode;
const DatabaseNode = DefaultNode;
const ApiCallNode = DefaultNode;
const ConditionNode = DefaultNode;
const DelayNode = DefaultNode;
const ScheduleNode = DefaultNode;
const TransformNode = DefaultNode;
const FilterNode = DefaultNode;
const AggregateNode = DefaultNode;
const ErrorHandlerNode = DefaultNode;

// Node component mapping
const NODE_COMPONENTS: Record<NodeType, React.ComponentType<NodeProps<WorkflowNodeData>>> = {
  aiAgent: AIAgentNode,
  webScraper: WebScraperNode,
  email: EmailNode,
  slack: SlackNode,
  notification: NotificationNode,
  data: DataNode,
  fileOperation: FileOperationNode,
  database: DatabaseNode,
  apiCall: ApiCallNode,
  condition: ConditionNode,
  delay: DelayNode,
  schedule: ScheduleNode,
  transform: TransformNode,
  filter: FilterNode,
  aggregate: AggregateNode,
  errorHandler: ErrorHandlerNode,
  instagram_post: InstagramPostNode
};

// Hook for managing node registry
export const useNodeRegistry = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load node registry from backend
  useEffect(() => {
    const loadRegistry = async () => {
      try {
        setIsLoading(true);
        const registry = await nodeRegistryService.getNodeRegistry();
        
        // Transform backend data to frontend format
        Object.entries(registry.nodes).forEach(([type, metadata]) => {
          NODE_TYPES[type] = {
            type: metadata.type,
            label: metadata.label,
            description: metadata.description,
            icon: metadata.icon,
            color: metadata.color,
            category: metadata.category
          };
        });
        
        setError(null);
      } catch (err) {
        console.error('Failed to load node registry:', err);
        setError('Failed to load node types from server');
        
        // Fallback to basic node types if backend fails
        NODE_TYPES['aiAgent'] = {
          type: 'aiAgent',
          label: 'AI Agent',
          description: 'AI-powered tasks (research, analysis, content generation)',
          icon: 'Bot',
          color: 'primary',
          category: 'AI & ML'
        };
        NODE_TYPES['instagram_post'] = {
          type: 'instagram_post',
          label: 'Instagram Post',
          description: 'Post content to Instagram Business accounts',
          icon: 'Instagram',
          color: 'pink',
          category: 'Social Media'
        };
      } finally {
        setIsLoading(false);
      }
    };

    loadRegistry();
  }, []);

  const getNodeComponent = (type: NodeType) => {
    return NODE_COMPONENTS[type] || DefaultNode;
  };

  const getNodeTypeInfo = (type: NodeType) => {
    return NODE_TYPES[type] || null;
  };

  const getAllNodeTypes = () => {
    return Object.keys(NODE_TYPES);
  };

  const getNodeTypesByCategory = () => {
    const categories: Record<string, string[]> = {};
    Object.values(NODE_TYPES).forEach(nodeType => {
      if (!categories[nodeType.category]) {
        categories[nodeType.category] = [];
      }
      categories[nodeType.category].push(nodeType.type);
    });
    return categories;
  };

  return {
    isLoading,
    error,
    getNodeComponent,
    getNodeTypeInfo,
    getAllNodeTypes,
    getNodeTypesByCategory,
    NODE_TYPES
  };
}; 